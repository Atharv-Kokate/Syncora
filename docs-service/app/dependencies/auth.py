import uuid
from fastapi import Header, HTTPException, status
import structlog

log = structlog.get_logger()

async def get_current_user(x_user_id: str = Header(None)) -> uuid.UUID:
    """
    FastAPI Dependency to extract the user identity from the headers.
    Because this service sits behind the API Gateway, the gateway is responsible
    for validating the JWT and injecting this exact header.
    
    If the header is missing or malformed, it means a bad internal request 
    or a misconfigured gateway proxy.
    """
    if not x_user_id:
        log.warning("missing_x_user_id_header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing identity header from Gateway",
        )
    
    try:
        # Validate it's a real UUID
        return uuid.UUID(x_user_id)
    except ValueError:
        log.warning("malformed_x_user_id_header", x_user_id=x_user_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid identity header format",
        )
