import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse
from app.repositories.document_repository import DocumentRepository
from app.services.document_service import DocumentService

# Note: The Gateway strips out the service name, so our route here is just "/"
# Gateway calls /api/docs/ -> we receive /
router = APIRouter(prefix="", tags=["Documents"])

def get_document_service(session: AsyncSession = Depends(get_db)) -> DocumentService:
    """Dependency Injection factory for the Service."""
    repo = DocumentRepository(session)
    return DocumentService(repo)


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document_in: DocumentCreate,
    current_user_id: uuid.UUID = Depends(get_current_user),
    docs_service: DocumentService = Depends(get_document_service)
):
    """Create a new document for the authenticated user."""
    return await docs_service.create_document(document_in, current_user_id)


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    current_user_id: uuid.UUID = Depends(get_current_user),
    docs_service: DocumentService = Depends(get_document_service)
):
    """List all documents owned by the authenticated user."""
    return await docs_service.list_user_documents(current_user_id)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    current_user_id: uuid.UUID = Depends(get_current_user),
    docs_service: DocumentService = Depends(get_document_service)
):
    """Retrieve a specific document, proving ownership."""
    return await docs_service.get_document(document_id, current_user_id)


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: uuid.UUID,
    document_update: DocumentUpdate,
    current_user_id: uuid.UUID = Depends(get_current_user),
    docs_service: DocumentService = Depends(get_document_service)
):
    """Update a document's title or JSON AST content."""
    return await docs_service.update_document(document_id, document_update, current_user_id)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    current_user_id: uuid.UUID = Depends(get_current_user),
    docs_service: DocumentService = Depends(get_document_service)
):
    """Delete a document entirely."""
    await docs_service.delete_document(document_id, current_user_id)
    return None
