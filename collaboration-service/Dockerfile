# ---------------------------------------------------------
# STAGE 1: Builder
# ---------------------------------------------------------
FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /build

# Install build dependencies (pycrdt uses Rust bindings, but pre-built wheels exist for linux)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------------------------------------------------------
# STAGE 2: Production Image
# ---------------------------------------------------------
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8003
ENV ENVIRONMENT=production

# The collaboration service connects to Redis and Docs Service
ENV REDIS_URL="redis://redis:6379/1"
ENV DOCS_SERVICE_URL="http://docs-service:8002"

RUN groupadd -r syncora && useradd -r -s /bin/false -g syncora syncora

WORKDIR /app

COPY --from=builder /install /usr/local

COPY app/ ./app/

RUN chown -R syncora:syncora /app
USER syncora

EXPOSE ${PORT}

# Uvicorn with standard workers; threads optimized for async IO and WebSockets
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 4 --proxy-headers
