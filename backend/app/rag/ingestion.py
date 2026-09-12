import hashlib
import logging
from pathlib import Path

from app.database.chroma import get_vector_store
from app.rag.loaders import load_document
from app.rag.chunker import chunk_documents


logger = logging.getLogger(__name__)


def generate_chunk_id(filename: str, chunk_index: int) -> str:

    raw_id = f"{filename}:{chunk_index}"

    return hashlib.sha256(raw_id.encode("utf-8")).hexdigest()


def ingest_document(file_path: str) -> dict:

    path = Path(file_path)

    logger.info("Starting ingestion: %s", path.name)

    # 1. LOAD DOCUMENT

    documents = load_document(str(path))

    if not documents:
        raise ValueError("The document contains no readable content.")

    logger.info(
        "Loaded %s document pages/sections",
        len(documents)
    )

    # 2. CHUNK DOCUMENT

    chunks = chunk_documents(documents)

    if not chunks:
        raise ValueError("No text chunks were generated from the document.")

    logger.info("Generated %s chunks", len(chunks))

    # 3. ADD COMMON METADATA

    for index, chunk in enumerate(chunks):

        chunk.metadata["filename"] = path.name
        chunk.metadata["chunk_index"] = index
        chunk.metadata["source"] = path.name

    # 4. GET VECTOR STORE

    vector_store = get_vector_store()

    # 5. REMOVE PREVIOUS VERSION

    try:

        vector_store.delete(
            where={"filename": path.name}
        )

        logger.info(
            "Removed previous vectors for %s",
            path.name
        )

    except Exception as exc:

        logger.warning(
            "Could not remove previous vectors: %s",
            exc
        )

    # 6. CREATE IDS

    ids = []

    for index, _chunk in enumerate(chunks):
        ids.append(generate_chunk_id(path.name, index))

    # 7. STORE IN CHROMADB

    vector_store.add_documents(
        documents=chunks,
        ids=ids
    )

    logger.info(
        "Successfully stored %s chunks for %s",
        len(chunks),
        path.name
    )

    # 8. RETURN INGESTION RESULT

    return {
        "success": True,
        "filename": path.name,
        "file_type": path.suffix.lower().replace(".", ""),
        "pages_or_sections": len(documents),
        "chunks": len(chunks),
        "message": (
            "Document successfully loaded, "
            "chunked, embedded, and stored in ChromaDB."
        )
    }