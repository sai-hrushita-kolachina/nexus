import logging
import shutil
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import get_settings
from app.database.sqlite import list_document_files, save_document_file
from app.rag.ingestion import ingest_document


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"]
)


# DIRECTORIES

DOCUMENTS_DIR = Path(get_settings().documents_directory)
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

    documents = [
        {
            "filename": item["filename"],
            "file_type": item["file_type"],
            "size_bytes": item["size_bytes"],
        }
        for item in list_document_files()
        if Path(item["filename"]).suffix.lower() in SUPPORTED_EXTENSIONS
    ]

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

        # KEEP A PERMANENT COPY IN THE DATABASE
        # (local disk is wiped on free hosting)
        save_document_file(
            filename=filename,
            file_type=extension.replace(".", ""),
            content=file_path.read_bytes(),
        )

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