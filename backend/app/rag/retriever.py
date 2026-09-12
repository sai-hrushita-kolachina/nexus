from app.config import get_settings
from app.database.chroma import get_vector_store


class Retriever:

    def __init__(self):
        self.settings = get_settings()
        self.vector_store = get_vector_store()

    def retrieve(self, query: str, k: int | None = None) -> list[dict]:

        if not query.strip():
            return []

        if k is None:
            k = self.settings.top_k

        results = self.vector_store.similarity_search_with_relevance_scores(
            query,
            k=k
        )

        retrieved = []

        for document, score in results:

            metadata = document.metadata or {}

            retrieved.append({
                "content": document.page_content,
                "score": float(score),
                "metadata": metadata
            })

        return retrieved