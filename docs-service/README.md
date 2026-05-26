# Syncora Docs Service

This is the Document Management microservice for Syncora. It is responsible for metadata management, document ownership logic, and storing snapshots of the document abstract syntax tree (AST).

## Architecture

This service lives entirely behind the API Gateway. The Gateway extracts and verifies JSON Web Tokens (JWT) and passes the downstream request with an `X-User-ID` header. This service inherently trusts that header, allowing for true microservice boundary separation and stateless scaling.

### Tech Stack
- Python 3.12
- FastAPI
- PostgreSQL (`asyncpg`)
- SQLAlchemy 2.0 (Async) & Alembic
- JSONB Columns

## Local Development

### Prerequisites
- Python 3.12+
- PostgreSQL database running locally

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
   uvicorn app.main:app --reload --port 8002
   ```

### Important Routing Note
Because this service is designed to be proxy-mounted under the Gateway's `/api/docs/` route, the endpoints in this service are mapped directly to `/`. 

For example, when running locally without the gateway:
- Creating a document: `POST http://localhost:8002/` 
  *(Requires `X-User-ID` header!)*
