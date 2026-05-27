import redis.asyncio as redis
from app.core.config import settings
import structlog

logger = structlog.get_logger()

# Global redis pool
_redis_client: redis.Redis | None = None

async def init_redis():
    """Initializes the global async Redis pool."""
    global _redis_client
    # CRITICAL: decode_responses=False because Yjs uses binary (Uint8Array) updates
    _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=False)
    
    # Ping to ensure connection
    await _redis_client.ping()
    logger.info("redis_connected", url=settings.REDIS_URL)

def get_redis() -> redis.Redis:
    """Gets the active Redis client."""
    if _redis_client is None:
        raise RuntimeError("Redis is not initialized. Call init_redis() first.")
    return _redis_client

async def close_redis():
    """Closes the Redis connection pool."""
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        logger.info("redis_disconnected")
