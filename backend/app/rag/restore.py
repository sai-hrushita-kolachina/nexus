import logging
from pathlib import Path

from app.config import get_settings
from app.database.chroma import get_vector_store
from app.database.sqlite import (get_document_file, list_document_files,)
from app.rag.ingestion import ingest_document


logger = logging.getLogger(__name__)


def restore_documents() -> None:
    documents_dir = Path(get_settings().documents_directory)
    documents_dir.mkdir(parents=True, exist_ok=True)

    try:
        files = list_document_files()
    except Exception:
        logger.exception("Could not read stored documents.")
        return

    if not files:
        logger.info("No stored documents to restore.")
        return

    vector_store = get_vector_store()

    for item in files:

        filename = item["filename"]

        try:
            existing = vector_store.get(
                where={"filename": filename},
                limit=1,
            )

            if existing.get("ids"):
                continue

            content = get_document_file(filename)

            if content is None:
                continue

            path = documents_dir / filename
            path.write_bytes(content)

            ingest_document(str(path))

            logger.info("Restored document: %s", filename)

        except Exception:
            logger.exception("Failed to restore document: %s", filename)

    logger.info("Document restore finished.")
