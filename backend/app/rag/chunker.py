from langchain_text_splitters import (RecursiveCharacterTextSplitter)
from app.config import get_settings


def chunk_documents(documents):
    settings = get_settings()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    chunks = splitter.split_documents(documents)

    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = index
    return chunks