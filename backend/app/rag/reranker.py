import re


class Reranker:

    @staticmethod
    def tokenize(text: str) -> set[str]:
        return set(re.findall(r"\b[a-zA-Z0-9]+\b", text.lower()))

    def rerank(self, query: str, results: list[dict], final_k: int = 5) -> list[dict]:

        if not results:
            return []

        query_terms = self.tokenize(query)
        reranked = []

        for result in results:

            content = result.get("content", "")
            content_terms = self.tokenize(content)

            if query_terms:
                overlap = len(query_terms & content_terms) / len(query_terms)
            else:
                overlap = 0.0

            hybrid_score = float(result.get("hybrid_score", 0.0))

            # FINAL SCORE

            final_score = 0.75 * hybrid_score + 0.25 * overlap

            result["term_overlap"] = overlap
            result["rerank_score"] = final_score

            reranked.append(result)

        reranked.sort(key=lambda item: item["rerank_score"], reverse=True)

        return reranked[:final_k]