from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
)


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".md",
}


def load_document(file_path: str):

    path = Path(file_path)
    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}. "
            f"Supported types: PDF, DOCX, TXT, MD."
        )

    # PDF

    if extension == ".pdf":
        loader = PyPDFLoader(str(path))

    # DOCX

    elif extension == ".docx":
        loader = Docx2txtLoader(str(path))

    # TXT / MARKDOWN

    else:
        loader = TextLoader(
            str(path),
            encoding="utf-8"
        )

    documents = loader.load()

    # NORMALIZE METADATA

    for document in documents:

        document.metadata["filename"] = path.name
        document.metadata["file_type"] = extension.replace(".", "")

        # PDF page numbers
        # PyPDFLoader uses zero-based page numbers.
        # We expose human-friendly 1-based page numbers.

        if extension == ".pdf":

            if "page" in document.metadata:
                document.metadata["page_number"] = int(
                    document.metadata["page"]
                ) + 1

            else:
                document.metadata["page_number"] = 1

        else:
            document.metadata["page_number"] = 1

    return documents