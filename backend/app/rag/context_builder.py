class ContextBuilder:
    def build(self, results: list[dict]) -> str:

        if not results:
            return (
                "No relevant company documents "
                "were found."
            )

        sections = []

        for index, result in enumerate(results, start=1):

            metadata = result.get("metadata", {})
            filename = metadata.get("filename", "Unknown document")

            page = metadata.get("page_number")

            score = result.get(
                "rerank_score", result.get("hybrid_score", 0.0)
            )

            if page:
                source = (f"{filename}, page {page}")

            else:
                source = filename
            content = result.get("content", "")

            sections.append(
                f"""
                    SOURCE {index}
                    Document: {source}
                    Relevance: {score:.2f}

                    Content:
                    {content}
                """
            )

        return "\n".join(sections)