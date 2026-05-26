# Expose models here so Alembic can discover them seamlessly 
from app.core.database import Base
from app.models.document import Document

__all__ = ["Base", "Document"]
