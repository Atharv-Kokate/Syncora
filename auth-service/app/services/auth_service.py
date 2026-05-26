from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool
import structlog

from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.token import TokenResponse
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.core import security, jwt

log = structlog.get_logger()

class AuthService:
    """
    Core business logic for Authentication.
    Coordinates between the Repository (Database) and Security components (Bcrypt/JWT).
    """
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_user(self, user_in: UserCreate) -> UserResponse:
        """
        Handles the registration flow:
        1. Checks if email is taken.
        2. Hashes the password (offloaded to threadpool).
        3. Saves user to database.
        """
        existing_user = await self.user_repo.get_by_email(user_in.email)
        if existing_user:
            log.warning("registration_failed_email_taken", email=user_in.email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered.",
            )

        # Offload CPU-heavy bcrypt hashing to a separate OS thread!
        # Do not block the async event loop constraint.
        hashed_pw = await run_in_threadpool(security.get_password_hash, user_in.password)

        new_user = User(
            email=user_in.email,
            hashed_password=hashed_pw
        )
        
        saved_user = await self.user_repo.create(new_user)
        log.info("user_registered_successfully", user_id=str(saved_user.id))
        
        return UserResponse.model_validate(saved_user)

    async def login_user(self, credentials: UserLogin) -> TokenResponse:
        """
        Handles the login flow:
        1. Checks if user exists.
        2. Verifies password hash (offloaded to threadpool).
        3. Mints a JWT if valid.
        """
        user = await self.user_repo.get_by_email(credentials.email)
        if not user or not user.is_active:
            log.warning("login_failed_user_not_found_or_inactive", email=credentials.email)
            # Use constant-timeish logic, but here we just error out to prevent enumeration 
            # Note: A pure security audit might want dummy password checks to prevent timing attacks.
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Offload CPU-heavy bcrypt verification to a separate OS thread
        is_password_valid = await run_in_threadpool(
            security.verify_password, credentials.password, user.hashed_password
        )

        if not is_password_valid:
            log.warning("login_failed_invalid_password", email=credentials.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Mint the stateless Access Token
        access_token = jwt.create_access_token(user_id=user.id)
        
        log.info("user_logged_in_successfully", user_id=str(user.id))
        return TokenResponse(access_token=access_token)
