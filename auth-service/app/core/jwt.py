from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import settings
import uuid

def create_access_token(user_id: uuid.UUID) -> str:
    """
    Injects the user's UUID into an encoded, signed JWT token.
    Uses HS256 to sign it against the secret.
    """
    # Expiration is securely minted inside the token itself
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 'sub' (subject) is the standard claim for identifying the user
    # 'exp' (expiration time) is standard, parsed natively by python-jose
    to_encode = {
        "sub": str(user_id),
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt
