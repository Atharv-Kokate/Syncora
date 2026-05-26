from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# 1. Create the asyncio engine
# echo=False in prod to prevent massive log spam, True in dev is helpful for debugging queries
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=(settings.ENVIRONMENT == "development"),
    future=True,
    pool_size=20,          # Base number of connections to keep open
    max_overflow=10,       # Allow scaling up to 30 temporarily under load
    pool_pre_ping=True,    # Verify connections are alive before using them (prevents 'MySQL server has gone away' style dropouts)
)

# 2. Create the Session Factory
async_session_maker = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False, # Essential for async execution so accessed attributes don't block
    autoflush=False
)

# 3. Base class for SQLAlchemy Models
class Base(DeclarativeBase):
    pass

# 4. FastAPI Dependency for database sessions
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to yield a database session per request.
    Automatically handles commit/rollback and closes the session
    after the request completes.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
