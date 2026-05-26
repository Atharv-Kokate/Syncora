from fastapi import APIRouter, Request, Depends
from app.core.config import settings
from app.dependencies.http_client import get_http_client
from app.services.proxy_service import forward_request
from app.middleware.rate_limit_middleware import limiter

router = APIRouter(prefix="/api/auth", tags=["Auth Service Proxy"])

# We allow wildcard paths here so the Gateway doesn't have to know
# about every single route that auth-service exposes
@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_WINDOW}seconds")
async def proxy_auth_requests(
    request: Request, 
    path: str,
    client = Depends(get_http_client)
):
    """
    Reverse proxy for the Auth service.
    Authentication is inherently NOT required to hit the auth service (e.g. login, register).
    """
    target_url = f"{settings.AUTH_SERVICE_URL}/api/auth/{path}"
    return await forward_request(request, target_url, client)
