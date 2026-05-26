from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_jwt_token

http_bearer = HTTPBearer()

async def require_auth(credentials: HTTPAuthorizationCredentials = Depends(http_bearer)) -> dict:
    """
    FastAPI Dependency to enforce JWT authentication on specific API routes.
    It expects an 'Authorization: Bearer <token>' header.
    Returns the decoded token payload (containing user_id, roles, etc).
    """
    return verify_jwt_token(credentials.credentials)

async def optional_auth(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))) -> dict | None:
    """
    FastAPI Dependency for routes where authentication is optional (e.g., fetching a public document).
    Returns the payload if a valid token is provided, else None.
    """
    if not credentials:
        return None
    return verify_jwt_token(credentials.credentials)