from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.schemas.token import TokenResponse
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    """
    Dependency Injection factory for the AuthService.
    It grabs the current database session, instances the repository, 
    and returns a fully wired service object.
    """
    repo = UserRepository(session)
    return AuthService(repo)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate, 
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user in the system.
    Validates email uniqueness and hashes the generated password.
    """
    return await auth_service.register_user(user_in)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    credentials: UserLogin, 
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate a user and return a JWT Access Token.
    Returns 401 if credentials are invalid.
    """
    return await auth_service.login_user(credentials)
