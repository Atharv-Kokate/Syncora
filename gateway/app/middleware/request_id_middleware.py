import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from contextvars import ContextVar

# Context variable to store the request ID globally for the current async task
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")

class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that ensures every request has an X-Correlation-ID.
    If the client/upstream didn't provide one, we generate a fresh UUID.
    This ID is injected into contextvars for our logger.
    """
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        # Set the correlation ID in the context for this request
        correlation_id_ctx.set(correlation_id)
        
        # Proceed with the request
        response = await call_next(request)
        
        # Inject the ID into the response headers so the client can trace it
        response.headers["X-Correlation-ID"] = correlation_id
        return response
