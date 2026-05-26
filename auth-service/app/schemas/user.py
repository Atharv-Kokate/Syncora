import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# ---------------------------------------------------------
# Request Schemas (Input Validation)
# ---------------------------------------------------------

class UserCreate(BaseModel):
    """
    Schema for validating user registration requests.
    Strict enforcing of email format and password strength.
    """
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long.")

class UserLogin(BaseModel):
    """
    Schema for validating login requests.
    """
    email: EmailStr
    password: str

# ---------------------------------------------------------
# Response Schemas (Output Serialization)
# ---------------------------------------------------------

class UserResponse(BaseModel):
    """
    Schema for serializing User data back to the client.
    Crucially, it EXCLUDES the hashed_password.
    """
    id: uuid.UUID
    email: EmailStr
    is_active: bool
    created_at: datetime

    # This tells Pydantic to read data directly from the SQLAlchemy Model attributes,
    # rather than expecting a physical Python dictionary.
    model_config = ConfigDict(from_attributes=True)
