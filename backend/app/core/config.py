"""Application configuration."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./autoapply.db"

    # JWT/Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # LLM
    LLM_PROVIDER: str = "openai"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4"
    LLM_TEMPERATURE: float = 0.7

    # Redis/Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"

    # Storage
    STORAGE_BACKEND: str = "local"  # local | s3
    STORAGE_PATH: str = "./storage"  # used for local backend
    STORAGE_S3_BUCKET: str = ""
    STORAGE_S3_REGION: str = ""
    STORAGE_S3_ENDPOINT_URL: str = ""  # e.g., for R2/MinIO

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
