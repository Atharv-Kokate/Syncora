from jose import jwt, JWTError
from fastapi import HTTPException, status
import structlog
from app.core.config import settings

log = structlog.get_logger()

def verify_jwt_token(token: str) -> dict:
    """
    Decodes and validates a JWT token using python-jose.
    If valid, returns the decoded payload.
    If invalid (expired, bad signature, etc.), raises a 401 HTTPException.
    """
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        log.warning("invalid_jwt_token", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
