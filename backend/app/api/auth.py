import logging
import bcrypt

from fastapi import APIRouter, Depends, HTTPException, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.config import get_settings
from app.database.sqlite import get_user_by_email, get_user_by_google_id, create_user
from app.models.auth import SignupRequest, LoginRequest, GoogleLoginRequest, AdminLoginRequest, AuthResponse
from app.utils.auth import create_access_token, get_current_user


# LOGGER

logger = logging.getLogger(__name__)


# SETTINGS

settings = get_settings()


# ROUTER

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


# PASSWORD HELPERS

def hash_password(password: str) -> str:
    """
    Hash a user's password using bcrypt.

    bcrypt has a maximum password input size of 72 bytes.
    We explicitly enforce that limit before hashing.
    """

    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must not exceed 72 bytes.",
        )

    password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    return password_hash.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a plain-text password against
    a stored bcrypt password hash.
    """

    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        return False

    try:
        return bcrypt.checkpw(password_bytes, password_hash.encode("utf-8"))

    except (ValueError, TypeError, bcrypt.BcryptError):
        return False


# USER RESPONSE HELPER

def build_user_response(user):
    """
    Convert a database user record into the
    safe user object returned to the frontend.

    Password hashes are NEVER returned.
    """

    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
    }


# EMPLOYEE SIGNUP

@router.post("/signup", response_model=AuthResponse)
def signup(request: SignupRequest):
    """
    Create a new employee account.
    """

    name = request.name.strip()
    email = request.email.strip().lower()
    password = request.password

    # Validate name

    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name is required.",
        )

    # Check existing account

    existing_user = get_user_by_email(email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # Hash password

    password_hash = hash_password(password)

    # Create employee

    user = create_user(
        name=name,
        email=email,
        password_hash=password_hash,
        google_id=None,
        auth_provider="local",
        role="employee",
    )

    # Create JWT

    access_token = create_access_token({
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
    })

    logger.info("New employee account created: %s", email)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": build_user_response(user),
    }


# EMPLOYEE LOGIN

@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest):
    """
    Login using email and password.
    """

    email = request.email.strip().lower()
    password = request.password

    # Find user

    user = get_user_by_email(email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # Only local accounts can use password login

    if not user.get("password_hash"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account uses Google Sign-In. Please continue with Google.",
        )

    # Verify password

    if not verify_password(password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # Create JWT

    access_token = create_access_token({
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
    })

    logger.info("Employee login successful: %s", email)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": build_user_response(user),
    }


# GOOGLE LOGIN

@router.post("/google", response_model=AuthResponse)
def google_login(request: GoogleLoginRequest):
    """
    Login or signup using Google Identity Services.

    The frontend sends Google's ID token/credential.
    The backend verifies it with Google before
    trusting the user's identity.
    """

    # Check Google Client ID configuration

    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google authentication is not configured on the server yet.",
        )

    # Verify Google token

    try:
        google_user = id_token.verify_oauth2_token(
            request.credential,
            google_requests.Request(),
            settings.google_client_id,
        )

    except ValueError:

        logger.warning("Invalid Google authentication token.")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google authentication token.",
        )

    # Verify email

    email = google_user.get("email")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account did not provide an email address.",
        )

    email_verified = google_user.get("email_verified", False)

    if not email_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google email address is not verified.",
        )

    # Get Google unique user ID

    google_id = google_user.get("sub")

    if not google_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account identifier is missing.",
        )

    email = email.strip().lower()

    # First search by Google ID

    user = get_user_by_google_id(google_id)

    # If Google ID does not exist,
    # check whether email already exists

    if not user:

        existing_user = get_user_by_email(email)

        if existing_user:

            if existing_user.get("auth_provider") == "local":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An account with this email already exists. Please login using your password.",
                )

            user = existing_user

        else:

            # Create new Google employee account

            name = google_user.get("name") or email.split("@")[0]

            user = create_user(
                name=name,
                email=email,
                password_hash=None,
                google_id=google_id,
                auth_provider="google",
                role="employee",
            )

            logger.info("New Google employee account created: %s", email)

    # Create application JWT

    access_token = create_access_token({
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
    })

    logger.info("Google login successful: %s", email)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": build_user_response(user),
    }


# CURRENT USER

@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    """
    Return the currently authenticated Nexus user.

    The frontend sends the Nexus JWT as:

        Authorization: Bearer <JWT>
    """

    return {
        "user": {
            "id": current_user["id"],
            "name": current_user["name"],
            "email": current_user["email"],
            "role": current_user["role"],
        }
    }


# ADMIN LOGIN

@router.post("/admin-login", response_model=AuthResponse)
def admin_login(request: AdminLoginRequest):
    """
    Login for authorized admins.

    Admin credentials are read from environment variables:

        ADMIN_EMAIL
        ADMIN_PASSWORD

    The admin does not use the employee users table.
    """

    email = request.email.strip().lower()
    password = request.password

    # Check server configuration

    if not settings.admin_email or not settings.admin_password:
        logger.error("Admin credentials are not configured.")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin authentication is not configured on the server.",
        )

    configured_email = settings.admin_email.strip().lower()

    # Check credentials

    if email != configured_email or password != settings.admin_password:
        logger.warning("Failed admin login attempt for: %s", email)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials.",
        )

    # Create admin JWT

    admin_user = {
        "id": "admin",
        "name": "Admin",
        "email": configured_email,
        "role": "admin",
    }

    access_token = create_access_token(admin_user)

    logger.info("Admin login successful: %s", configured_email)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": "admin",
            "name": "Admin",
            "email": configured_email,
            "role": "admin",
        },
    }