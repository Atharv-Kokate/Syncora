from fastapi import APIRouter, Request, Depends
from app.core.config import settings
from app.dependencies.http_client import get_http_client
from app.dependencies.auth_dependency import require_auth
from app.services.proxy_service import forward_request
from app.middleware.rate_limit_middleware import limiter

router = APIRouter(prefix="/api/collab", tags=["Collaboration Service Proxy"])

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_WINDOW}seconds")
async def proxy_collab_requests(
    request: Request, 
    path: str,
    user_payload: dict = Depends(require_auth), 
    client = Depends(get_http_client)
):
    """
    Reverse proxy for the Collaboration service.
    (Note: Standard HTTP proxy logic here. WebSockets will require a dedicated path
    or different protocol upgrade logic in the future).
    """
    request.state.user_payload = user_payload
    target_url = f"{settings.COLLAB_SERVICE_URL}/api/collab/{path}"
    return await forward_request(request, target_url, client)
