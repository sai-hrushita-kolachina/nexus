import logging
import shutil
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.rag.ingestion import ingest_document


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"]
)


# DIRECTORIES

BASE_DIR = Path(__file__).resolve().parents[2]
DOCUMENTS_DIR = BASE_DIR / "data" / "documents"

DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".md",
}


# LIST DOCUMENTS

@router.get("")
def list_documents():

    documents = []

    for file_path in DOCUMENTS_DIR.iterdir():

        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        documents.append({
            "filename": file_path.name,
            "file_type": file_path.suffix.replace(".", "").lower(),
            "size_bytes": file_path.stat().st_size
        })

    return {
        "documents": documents
    }


# UPLOAD DOCUMENT

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )

    filename = Path(file.filename).name
    extension = Path(filename).suffix.lower()

    # VALIDATE FILE TYPE

    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}. Supported files are PDF, DOCX, TXT and MD."
        )

    file_path = DOCUMENTS_DIR / filename

    try:

        # SAVE FILE

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info("Uploaded document: %s", filename)

        # INGEST DOCUMENT

        result = ingest_document(str(file_path))

        return result

    except ValueError as exc:

        # Remove invalid file

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:

        logger.exception(
            "Document ingestion failed: %s",
            filename
        )

        raise HTTPException(
            status_code=500,
            detail="Document upload succeeded, but ingestion failed. Check backend logs."
        )