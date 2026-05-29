from fastapi import APIRouter, Request, Depends
from app.core.config import settings
from app.dependencies.http_client import get_http_client
from app.dependencies.auth_dependency import require_auth
from app.services.proxy_service import forward_request
from app.middleware.rate_limit_middleware import limiter

router = APIRouter(prefix="/api/docs", tags=["Docs Service Proxy"])

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_WINDOW}seconds")
async def proxy_docs_requests(
    request: Request, 
    path: str,
    # Inject JWT verification here. If token is missing/invalid, 
    # it throws 401 before hitting downstream.
    user_payload: dict = Depends(require_auth), 
    client = Depends(get_http_client)
):
    """
    Reverse proxy for the Docs service.
    Requires a valid JWT token.
    Throws the payload into request.state so the proxy service can extract it.
    """
    request.state.user_payload = user_payload
    target_url = f"{settings.DOCS_SERVICE_URL}/{path}"
    return await forward_request(request, target_url, client)
