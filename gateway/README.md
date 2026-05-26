# Syncora API Gateway

This is the centralized API Gateway for the Syncora platform. It is a highly-concurrent, async-first reverse proxy built with FastAPI and HTTPX.

## Responsibilities
- **Reverse Proxying:** Forwards requests to downstream microservices seamlessly.
- **Unified Authentication:** Intercepts and parses JWTs for protected routes so internal services don't have to.
- **Rate Limiting:** IP-based request throttling using SlowAPI and Redis.
- **Observability:** Centralized JSON logging via `structlog` and correlation ID injection.

## Tech Stack
- Python 3.12 
- FastAPI
- Uvicorn
- HTTPX
- Structlog

## Local Development

### Prerequisites
- Python 3.12+
- Redis (Optional, falls back to memory if unavailable)

### Setup
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

## Production Deployment (Docker)

This service is packaged using a multi-stage Dockerfile for minimal image bloat and runs as a secure non-root user.

### Build
```bash
docker build -t syncora-gateway:latest .
```

### Run
```bash
docker run -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e JWT_SECRET="your_production_secret" \
  -e REDIS_URL="redis://your-redis-host:6379/0" \
  -e AUTH_SERVICE_URL="http://auth-service:8001" \
  -e DOCS_SERVICE_URL="http://docs-service:8002" \
  -e COLLAB_SERVICE_URL="http://collab-service:8003" \
  syncora-gateway:latest
```

## Architectural Notes
- The gateway streams responses from downstream services rather than buffering massive JSON blocks in memory, keeping memory consumption low.
- Middlewares are executed hierarchically: CORS → Rate Limiting → Logging → Request ID Correlation.
