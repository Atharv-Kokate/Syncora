from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    PORT: int = 8000

    # Service URLs
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    DOCS_SERVICE_URL: str = "http://localhost:8002"
    COLLAB_SERVICE_URL: str = "http://localhost:8003"
    COLLAB_SERVICE_WS_URL: str = "ws://localhost:8003"
    
    # Security
    JWT_SECRET: str = "super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60 # seconds
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
