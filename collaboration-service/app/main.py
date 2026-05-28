from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging
import structlog
from contextlib import asynccontextmanager
from app.core.redis_client import init_redis, close_redis
from app.services.pubsub_manager import pubsub_manager
from app.routes.ws_routes import router as ws_router
import structlog

# Initialize structured logging
setup_logging()
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize shared resources (Phase 2 Redis will go here)
    logger.info("collaboration_service_starting", env=settings.ENVIRONMENT)
    
    # Initialize Redis connection pool
    await init_redis()
    
    # Start the Redis Pub/Sub listener background task
    await pubsub_manager.connect()
    
    yield
    
    # Shutdown: Clean up resources
    logger.info("collaboration_service_shutting_down")
    await pubsub_manager.disconnect()
    await close_redis()

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)
app.include_router(ws_router)

@app.get("/health")
async def health_check():
    """Basic health check for Docker/Kubernetes probes."""
    return {"status": "ok", "service": "collaboration-service"}
