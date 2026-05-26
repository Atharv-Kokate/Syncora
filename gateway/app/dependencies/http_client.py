from fastapi import Request
import httpx

def get_http_client(request: Request) -> httpx.AsyncClient:
    """
    FastAPI dependency to retrieve the global async HTTP client
    initialized during the app lifecycle. This prevents us from 
    creating new connection pools per-request.
    """
    return request.app.state.http_client
