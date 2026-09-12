from pydantic import BaseModel

class DocumentMetadata(BaseModel):
    filename: str
    department: str | None = None
    document_type: str | None = None
    pages: int | None = None
    chunks: int | None = None

class DocumentResponse(BaseModel):
    success: bool
    message: str
    document: DocumentMetadata | None = None