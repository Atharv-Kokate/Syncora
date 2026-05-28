from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logger import setup_logger
from app.core.database import engine
from app.models.document import Base
from app.routes import document_routes

setup_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Perform startup operations
    # Auto-create tables for development
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    yield
    # Graceful shutdown: cleanup database pool
    await engine.dispose()

app = FastAPI(
    title="Syncora Docs Service",
    description="Document metadata and snapshot service for Syncora",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan
)

app.include_router(document_routes.router)

@app.get("/health")
async def health_check():
    """Liveness probe"""
    return {"status": "healthy", "service": "docs-service"}

