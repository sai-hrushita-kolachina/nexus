from functools import lru_cache
from langchain_community.embeddings import FastEmbedEmbeddings
from app.config import get_settings

@lru_cache
def get_embeddings():
    settings = get_settings()

    embeddings = FastEmbedEmbeddings(
        model_name=settings.embedding_model,
        threads=1,
        batch_size=32,
    )

    return embeddings