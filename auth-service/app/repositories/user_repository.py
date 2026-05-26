from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

class UserRepository:
    """
    Data Access Layer (Repository Pattern).
    Isolates all SQLAlchemy interactions so the business logic (Service)
    doesn't know about the underlying database technology.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        """Fetch a user by their exact email, returning None if not found."""
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user_obj: User) -> User:
        """Insert a newly constructed User object into the database."""
        self.session.add(user_obj)
        # Note: We flush here to ensure the DB assigns an ID or validates constraints.
        # The actual commit happens inside the base Dependency (`get_db`) upon route success.
        await self.session.flush()
        await self.session.refresh(user_obj)
        return user_obj
