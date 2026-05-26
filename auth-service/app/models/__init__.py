# Expose models here so Alembic can discover them seamlessly 
# when it imports app.models
from app.core.database import Base
from app.models.user import User

__all__ = ["Base", "User"]
