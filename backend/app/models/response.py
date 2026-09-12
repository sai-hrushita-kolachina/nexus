from pydantic import BaseModel, Field

class Source(BaseModel):
    filename: str
    page: int | None = None
    relevance: float = 0.0

class ChatResponse(BaseModel):
    answer: str
    query_type: str
    provider: str | None = None
    sources: list[Source] = Field(default_factory = list)

    conversation_id: str | None = None
    retrieval_relevance: float | None = None