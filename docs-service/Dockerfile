# ---------------------------------------------------------
# STAGE 1: Builder
# ---------------------------------------------------------
FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /build

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------------------------------------------------------
# STAGE 2: Production Image
# ---------------------------------------------------------
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8002
ENV ENVIRONMENT=production

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd -r syncora && useradd -r -s /bin/false -g syncora syncora

WORKDIR /app

COPY --from=builder /install /usr/local

COPY alembic.ini .
COPY alembic/ ./alembic/
COPY app/ ./app/

RUN chown -R syncora:syncora /app
USER syncora

EXPOSE ${PORT}

# Start the server (Tables are auto-created in main.py lifespan for now)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 4 --proxy-headers
