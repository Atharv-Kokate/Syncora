import uuid
from typing import List
from fastapi import HTTPException, status
import structlog

from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse
from app.models.document import Document
from app.repositories.document_repository import DocumentRepository

log = structlog.get_logger()

class DocumentService:
    """
    Core business logic for Documents.
    Enforces ownership permissions securely before saving/retrieving data.
    """
    def __init__(self, document_repo: DocumentRepository):
        self.document_repo = document_repo

    async def create_document(self, document_in: DocumentCreate, user_id: uuid.UUID) -> DocumentResponse:
        """Creates a document rigidly associating it to the requester's ID."""
        new_doc = Document(
            title=document_in.title,
            content=document_in.content,
            owner_id=user_id
        )
        saved_doc = await self.document_repo.create(new_doc)
        log.info("document_created_successfully", document_id=str(saved_doc.id), owner_id=str(user_id))
        return DocumentResponse.model_validate(saved_doc)

    async def get_document(self, document_id: uuid.UUID, user_id: uuid.UUID) -> DocumentResponse:
        """Fetches a document and vehemently ensures the user owns it."""
        doc = await self.document_repo.get_by_id(document_id)
        
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
            
        if doc.owner_id != user_id:
            log.warning("unauthorized_document_access_attempt", document_id=str(document_id), user_id=str(user_id))
            # Return 404 instead of 403 to prevent fishing attempts determining if documents exist
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
            
        return DocumentResponse.model_validate(doc)

    async def list_user_documents(self, user_id: uuid.UUID) -> List[DocumentResponse]:
        """Provides a dashboard view of all documents for the calling user."""
        docs = await self.document_repo.list_by_owner(user_id)
        return [DocumentResponse.model_validate(doc) for doc in docs]

    async def update_document(self, document_id: uuid.UUID, update_in: DocumentUpdate, user_id: uuid.UUID) -> DocumentResponse:
        """Enforces ownership and executes a partial update (PATCH) of fields."""
        doc = await self.document_repo.get_by_id(document_id)
        
        if not doc or doc.owner_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        # Dynamically apply changes only if sent in payload
        if update_in.title is not None:
            doc.title = update_in.title
        if update_in.content is not None:
            doc.content = update_in.content
            
        # SQLAlchemy tracks the modifications natively on the instanced object.
        # It'll auto-commit when the dependency yields via flush() mechanisms.
        await self.document_repo.session.flush()
        
        log.info("document_updated_successfully", document_id=str(doc.id))
        return DocumentResponse.model_validate(doc)

    async def delete_document(self, document_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Enforces ownership and deletes the document permanently."""
        doc = await self.document_repo.get_by_id(document_id)
        
        if not doc or doc.owner_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
            
        await self.document_repo.delete(document_id)
        log.info("document_deleted_successfully", document_id=str(document_id))
