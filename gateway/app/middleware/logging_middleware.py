import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import structlog
from app.middleware.request_id_middleware import correlation_id_ctx

log = structlog.get_logger()

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs incoming requests and their responses,
    automatically binding the correlation ID from contextvars to the log entry.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        # Bind context ID to everything logged within this request lifecycle
        request_id = correlation_id_ctx.get()
        bound_logger = log.bind(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None
        )

        bound_logger.info("request_started")
        
        try:
            response = await call_next(request)
            process_time = time.perf_counter() - start_time
            status_code = response.status_code
            
            bound_logger.info(
                "request_finished",
                status_code=status_code,
                duration_ms=round(process_time * 1000, 2)
            )
            return response
            
        except Exception as e:
            process_time = time.perf_counter() - start_time
            bound_logger.error(
                "request_failed",
                error=str(e),
                duration_ms=round(process_time * 1000, 2)
            )
            # Re-raise to let exception handlers manage it
            raise
