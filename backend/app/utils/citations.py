from app.models.response import Source


def build_citations(results: list[dict]) -> list[Source]:

    citations = []
    seen = set()

    for result in results:

        metadata = result.get("metadata", {})

        filename = metadata.get("filename", "Unknown document")

        page = metadata.get("page_number")

        if page is None:
            page = metadata.get("page")

        if page is not None:

            try:
                page = int(page)

            except (TypeError, ValueError):
                page = None

        relevance = result.get(
            "rerank_score",
            result.get("hybrid_score", 0.0)
        )

        try:
            relevance = float(relevance)

        except (TypeError, ValueError):
            relevance = 0.0

        citation_key = (filename, page)

        if citation_key in seen:
            continue

        seen.add(citation_key)

        citations.append(
            Source(
                filename=filename,
                page=page,
                relevance=round(relevance, 3)
            )
        )

    return citations