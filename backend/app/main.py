import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database.sqlite import initialize_database
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.history import router as history_router
from app.api.health import router as health_router
from app.utils.auth import get_current_user, require_admin


# LOGGING

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)


# SETTINGS

settings = get_settings()


# FASTAPI APPLICATION

app = FastAPI(
    title=settings.app_name,
    description="Full-stack company knowledge assistant with RAG and multi-LLM orchestration.",
    version="1.0.0"
)


# DATABASE STARTUP

@app.on_event("startup")
def startup_event():

    logging.getLogger(__name__).info("Initializing SQLite database...")

    initialize_database()

    logging.getLogger(__name__).info("SQLite database initialized successfully.")


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.vite_frontend_url,
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# PUBLIC ROUTES

# Health check does NOT require authentication.
app.include_router(health_router)

# Login / Signup / Google Login / Admin Login
# must remain PUBLIC because users need these endpoints
# before they have a JWT token.
app.include_router(auth_router)


# AUTHENTICATED USER ROUTES

# Any authenticated employee or admin can use chat.
app.include_router(
    chat_router,
    dependencies=[Depends(get_current_user)]
)

# Any authenticated employee or admin can view
# their conversation history.
app.include_router(
    history_router,
    dependencies=[Depends(get_current_user)]
)



# ADMIN-ONLY ROUTES
# Only users whose JWT contains role="admin"
# can access document management.
app.include_router(
    documents_router,
    dependencies=[Depends(require_admin)]
)


# ROOT ENDPOINT

@app.get("/")
def root():

    return {
        "application": settings.app_name,
        "status": "running",
        "message": "Nexus backend is running.",
        "version": "1.0.0"
    }