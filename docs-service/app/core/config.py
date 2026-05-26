from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    PORT: int = 8002
    
    # Database Configuration (Separate database for this microservice)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/syncora_docs"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
