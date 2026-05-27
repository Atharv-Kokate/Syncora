from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Syncora Collab Service"
    ENVIRONMENT: str = "development"
    REDIS_URL: str = "redis://localhost:6379/1"  # Database 1 for pub/sub
    DOCS_SERVICE_URL: str = "http://localhost:8002"

    class Config:
        env_file = ".env"

settings = Settings()
