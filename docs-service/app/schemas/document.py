import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------

class DocumentCreate(BaseModel):
    """Payload to create a new document."""
    title: Optional[str] = Field(default="Untitled Document", max_length=255)
    content: Optional[Dict[str, Any]] = Field(default_factory=dict)

class DocumentUpdate(BaseModel):
    """Payload to update an existing document."""
    # Using Optional allows partial updates (PATCH)
    title: Optional[str] = Field(default=None, max_length=255)
    content: Optional[Dict[str, Any]] = Field(default=None)

# ---------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------

class DocumentResponse(BaseModel):
    """Payload returned to the client representing a Document."""
    id: uuid.UUID
    title: str
    content: Dict[str, Any]
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    # Tells Pydantic to read from SQLAlchemy object attributes
    model_config = ConfigDict(from_attributes=True)
