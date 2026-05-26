import uuid
from typing import Sequence
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document

class DocumentRepository:
    """
    Data Access Layer isolating SQLAlchemy from business logic.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, document_obj: Document) -> Document:
        """Insert a newly constructed Document."""
        self.session.add(document_obj)
        await self.session.flush()
        await self.session.refresh(document_obj)
        return document_obj

    async def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        """Fetch a document by its exact UUID."""
        stmt = select(Document).where(Document.id == document_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_owner(self, owner_id: uuid.UUID) -> Sequence[Document]:
        """Fetch all documents belonging to a specific user."""
        stmt = select(Document).where(Document.owner_id == owner_id).order_by(Document.updated_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete(self, document_id: uuid.UUID) -> None:
        """Physically delete a document."""
        stmt = delete(Document).where(Document.id == document_id)
        await self.session.execute(stmt)
        # Flush to ensure the deletion executes immediately within the transaction
        await self.session.flush()
