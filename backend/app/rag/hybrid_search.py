import re

from rank_bm25 import BM25Okapi

from app.config import get_settings
from app.database.chroma import get_vector_store


class HybridSearch:

    def __init__(self):
        self.settings = get_settings()
        self.vector_store = get_vector_store()

    # TOKENIZATION

    @staticmethod
    def tokenize(text: str) -> list[str]:
        return re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())

    # LOAD ALL DOCUMENT CHUNKS

    def _load_all_chunks(self):

        data = self.vector_store.get(
            include=["documents", "metadatas"]
        )

        documents = data.get("documents", [])
        metadatas = data.get("metadatas", [])

        chunks = []

        for index, content in enumerate(documents):

            if not content:
                continue

            metadata = {}

            if index < len(metadatas):
                metadata = metadatas[index] or {}

            chunks.append({
                "content": content,
                "metadata": metadata
            })

        return chunks

    # NORMALIZE SCORES

    @staticmethod
    def normalize_scores(scores: dict) -> dict:

        if not scores:
            return {}

        minimum = min(scores.values())
        maximum = max(scores.values())

        if maximum == minimum:
            return {key: 1.0 for key in scores}

        return {
            key: (value - minimum) / (maximum - minimum)
            for key, value in scores.items()
        }

    # HYBRID SEARCH

    def search(
        self,
        query: str,
        k: int | None = None
    ) -> list[dict]:

        if not query.strip():
            return []

        if k is None:
            k = self.settings.top_k

        # VECTOR SEARCH

        vector_results = self.vector_store.similarity_search_with_relevance_scores(
            query,
            k=k
        )

        combined = {}

        for document, score in vector_results:

            metadata = document.metadata or {}

            filename = metadata.get("filename", "unknown")
            chunk_index = metadata.get("chunk_index", 0)

            key = f"{filename}:{chunk_index}"

            combined[key] = {
                "content": document.page_content,
                "metadata": metadata,
                "vector_score": float(score),
                "keyword_score": 0.0
            }

        # BM25 SEARCH

        all_chunks = self._load_all_chunks()

        if all_chunks:

            corpus = [
                self.tokenize(chunk["content"])
                for chunk in all_chunks
            ]

            bm25 = BM25Okapi(corpus)

            query_tokens = self.tokenize(query)

            keyword_scores = bm25.get_scores(query_tokens)

            keyword_mapping = {}

            for index, score in enumerate(keyword_scores):

                if index >= len(all_chunks):
                    continue

                chunk = all_chunks[index]
                metadata = chunk["metadata"]

                filename = metadata.get("filename", "unknown")
                chunk_index = metadata.get("chunk_index", index)

                key = f"{filename}:{chunk_index}"

                keyword_mapping[key] = float(score)

            normalized_keyword_scores = self.normalize_scores(
                keyword_mapping
            )

            # ADD BM25-ONLY RESULTS

            sorted_keyword = sorted(
                normalized_keyword_scores.items(),
                key=lambda item: item[1],
                reverse=True
            )

            for key, score in sorted_keyword[:k]:

                if key in combined:

                    combined[key]["keyword_score"] = score

                else:

                    # Find original chunk
                    for chunk in all_chunks:

                        metadata = chunk["metadata"]

                        filename = metadata.get("filename", "unknown")
                        chunk_index = metadata.get("chunk_index", 0)

                        current_key = f"{filename}:{chunk_index}"

                        if current_key == key:

                            combined[key] = {
                                "content": chunk["content"],
                                "metadata": metadata,
                                "vector_score": 0.0,
                                "keyword_score": score
                            }

                            break

        # HYBRID SCORE

        for item in combined.values():

            vector_score = item["vector_score"]
            keyword_score = item["keyword_score"]

            # Semantic search gets slightly more weight.
            item["hybrid_score"] = (
                0.65 * vector_score
                + 0.35 * keyword_score
            )

        # SORT

        results = sorted(
            combined.values(),
            key=lambda item: item["hybrid_score"],
            reverse=True
        )

        return results[:k]