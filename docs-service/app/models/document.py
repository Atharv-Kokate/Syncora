import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Document(Base):
    """
    SQLAlchemy 2.0 model representing a document.
    """
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), default="Untitled Document")
    
    # We use PostgreSQL's native JSONB. This allows us to store the document's rich-text 
    # AST (Abstract Syntax Tree) efficiently without converting to raw strings.
    # It also enables fast indexing and querying inside the JSON structure if needed later.
    content: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # This associates the document with a user from the `auth-service`.
    # Notice there is NO ForeignKey constraint here, because the `users` table
    # physically lives in a completely different microservice database.
    owner_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
    )
