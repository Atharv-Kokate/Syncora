# ---------------------------------------------------------
# STAGE 1: Builder
# ---------------------------------------------------------
FROM python:3.12-slim-bookworm AS builder

# Prevent Python from writing pyc files to disk and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /build

# Install system dependencies required for building pip packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Install python dependencies into a local directory for copying
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------------------------------------------------------
# STAGE 2: Production Image
# ---------------------------------------------------------
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Bind port 8000 by default
ENV PORT=8000
# Force production logging and settings by default
ENV ENVIRONMENT=production

# Create a non-root user and group
RUN groupadd -r syncora && useradd -r -s /bin/false -g syncora syncora

WORKDIR /app

# Copy the compiled dependencies from the builder stage
COPY --from=builder /install /usr/local

# Copy the actual application code
COPY app/ ./app/

# Change ownership of the app directory to the non-root user
RUN chown -R syncora:syncora /app

# Switch to the non-root user
USER syncora

EXPOSE ${PORT}

# Use uvicorn to run the app. 
# In a highly concurrent prod environment, we would use Gunicorn with Uvicorn workers,
# but for a purely async HTTPX proxy, raw Uvicorn is highly efficient.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 4 --proxy-headers
