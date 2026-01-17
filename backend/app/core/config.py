"""Application configuration from environment variables."""
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration loaded from .env file."""

    # Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    CORS_ORIGINS: List[str] = ["*"]

    # Database
    DATABASE_URL: str = "sqlite:///./autoapply.db"

    # Security
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # LLM (future)
    LLM_PROVIDER: str = "openai"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4"
    LLM_TEMPERATURE: float = 0.7

    # Background Tasks (future)
    REDIS_URL: str = "redis://localhost:6379/0"

    # File Storage
    STORAGE_PATH: str = "./storage"

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
