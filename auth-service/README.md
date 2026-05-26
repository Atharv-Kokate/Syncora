# Syncora Auth Service

This is the Identity Management microservice for Syncora. It is responsible for user registration, password verification, and minting JWT Access Tokens.

## Tech Stack
- Python 3.12
- FastAPI
- PostgreSQL (via `asyncpg`)
- SQLAlchemy 2.0 (Async)
- Alembic (Migrations)
- Passlib (Bcrypt hashing)
- Python-JOSE (JWT)

## Local Development

### Prerequisites
- Python 3.12+
- PostgreSQL database running locally (e.g., via Docker)

### Setup
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run migrations to build the database schema:
   ```bash
   # First time setup: Generate the initial migration script based on models
   alembic revision --autogenerate -m "Initial Create"
   
   # Apply it to the database
   alembic upgrade head
   ```
4. Run the development server:
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

## Architectural Notes
- **Database Threading:** Uses native `asyncpg` bindings. Standard SQLAlchemy creates blocking OS threads; this approach utilizes an asyncio event loop for massive IO parallelization.
- **CPU Isolation:** Bcrypt hashing intentionally takes ~300ms. These commands are wrapped in `fastapi.concurrency.run_in_threadpool()` so they don't freeze the concurrent event loop for other users.
- **Stateless Tokens:** Access tokens are cryptographically signed and stateless. Revisions/revocations will be handled via Gateway-level blocklists in future implementations.
