from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):

    # APPLICATION
    app_name: str = "Nexus"
    environment: str = "development"

    backend_host: str = "0.0.0.0"
    backend_port: int = 4000

    vite_frontend_url: str


    # GEMINI
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.5-flash-lite"


    # GROQ
    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"


    # RAG
    embedding_model: str = (
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    chroma_persist_directory: str = "./data/chroma"
    chroma_collection_name: str = "company_knowledge"
    documents_directory: str = "./data/documents"

    chunk_size: int = 800
    chunk_overlap: int = 120

    top_k: int = 8
    final_k: int = 5

    min_relevance_score: float = 0.30

    database_url: str | None = None

    # SQLITE (local development fallback)
    sqlite_database: str = "./data/company_ai.db"


    # JWT AUTHENTICATION
    jwt_secret_key: str = "CHANGE_THIS_IN_ENV"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60


    # GOOGLE AUTHENTICATION
    google_client_id: str | None = None


    # ADMIN AUTHENTICATION
    admin_email: str | None = None
    admin_password: str | None = None


    # PYDANTIC SETTINGS
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# SETTINGS INSTANCE
@lru_cache
def get_settings() -> Settings:
    return Settings()