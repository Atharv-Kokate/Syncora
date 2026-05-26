import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class User(Base):
    """
    Core SQLAlchemy 2.0 model representing a user in the database.
    Uses UUID4 natively for ID generation to avoid sequence guessing.
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    
    # We DO NOT store plain text passwords. This stores the bcrypt hash.
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Allows soft-deleting or banning users
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timezone-aware audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
    )
