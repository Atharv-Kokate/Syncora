from passlib.context import CryptContext

# Set up bcrypt as the hashing algorithm.
# Deprecated algorithms are removed from auto-evaluation for security.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a stored bcrypt hash.
    NOTE: bcrypt is CPU intensive. When calling this from an async endpoint,
    always run it via fastapi.concurrency.run_in_threadpool.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hashes a plain text password using bcrypt.
    NOTE: bcrypt is CPU intensive. When calling this from an async endpoint,
    always run it via fastapi.concurrency.run_in_threadpool.
    """
    return pwd_context.hash(password)
