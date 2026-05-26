from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI
from app.core.config import settings
import redis.asyncio as redis
import structlog

log = structlog.get_logger()

def get_limiter() -> Limiter:
    """
    Initializes the SlowAPI limiter.
    For production, we connect this to an async Redis cluster.
    If Redis isn't immediately available during local dev, slowapi gracefully falls back to in-memory,
    though we are directly initializing it with Redis assumptions for production-readiness.
    """
    try:
        # We attempt to connect to Redis for distributed rate limiting.
        redis_store = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=[f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_WINDOW}seconds"],
            storage_uri=settings.REDIS_URL
        )
    except Exception as e:
        log.warning("redis_connection_failed_falling_back_to_memory_rate_limiting", error=str(e))
        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=[f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_WINDOW}seconds"]
        )
    
    return limiter

limiter = get_limiter()

def setup_rate_limiting(app: FastAPI):
    """
    Registers the SlowAPI exception handler with the FastAPI app,
    which ensures standardized 429 Too Many Requests responses.
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
