from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logger import setup_logger
from app.core.database import engine
from app.routes import auth_routes

setup_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Perform startup operations
    # In a prod environment, checking DB connection explicitly here is a good idea
    yield
    # Graceful shutdown: cleanup database pool
    await engine.dispose()

app = FastAPI(
    title="Syncora Auth Service",
    description="Identity management service for Syncora",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan
)

app.include_router(auth_routes.router)

@app.get("/health")
async def health_check():
    """Liveness probe"""
    return {"status": "healthy", "service": "auth-service"}

