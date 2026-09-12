from functools import lru_cache
from pathlib import Path

from langchain_chroma import Chroma

from app.config import get_settings
from app.rag.embeddings import get_embeddings


@lru_cache
def get_vector_store():

    settings = get_settings()

    persist_directory = Path(
        settings.chroma_persist_directory
    )

    persist_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    vector_store = Chroma(
        collection_name=settings.chroma_collection_name,

        embedding_function=get_embeddings(),

        persist_directory=str(
            persist_directory
        )
    )

    return vector_store