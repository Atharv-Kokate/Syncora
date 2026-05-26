from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import httpx
from app.core.config import settings
from app.core.logger import setup_logger
from app.middleware.request_id_middleware import RequestIDMiddleware
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.rate_limit_middleware import setup_rate_limiting
from app.routes import health_routes, auth_routes, docs_routes, collaboration_routes

# 1. Initialize core dependencies (like structured logging)
setup_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles the startup and shutdown lifecycle of the Gateway.
    We create a global HTTP client pool here to avoid socket exhaustion.
    """
    app.state.http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(timeout=15.0), # Stricter timeout for gateway proxying
        limits=httpx.Limits(max_keepalive_connections=100, max_connections=500)
    )
    yield
    # Graceful shutdown of the client pool
    await app.state.http_client.aclose()

# 2. Create the FastAPI app
app = FastAPI(
    title="Syncora API Gateway",
    description="The centralized API Gateway for the Syncora platform",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan
)

# 3. Setup Rate Limiting (SlowAPI)
setup_rate_limiting(app)

# 4. Add middlewares (Order matters!)
# CORS should be the outermost middleware so preflight OPTIONS requests return immediately.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

# 5. Include Routers
app.include_router(health_routes.router)
app.include_router(auth_routes.router)
app.include_router(docs_routes.router)
app.include_router(collaboration_routes.router)


# To run locally: uvicorn app.main:app --reload --port 8000
