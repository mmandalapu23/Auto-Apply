"""Job source configuration and management model."""
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Boolean, Integer
from sqlalchemy.sql import func

from backend.app.db.base import Base


class JobSource(Base):
    """Track job sources and their configuration."""

    __tablename__ = "job_sources"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String(50), unique=True, nullable=False, index=True)  # greenhouse, wellfound, flexjobs, workday
    display_name: str = Column(String(100), nullable=False)  # "Greenhouse", "Wellfound", etc.
    api_endpoint: str = Column(String(500), nullable=True)  # API URL or domain
    api_key: str = Column(String(500), nullable=True)  # Encrypted API key
    is_enabled: bool = Column(Boolean, default=True, index=True)
    is_configured: bool = Column(Boolean, default=False)  # Has API key been set?
    last_sync_at: datetime = Column(DateTime, nullable=True)  # Last successful sync
    last_sync_status: str = Column(String(50), default="pending")  # pending, success, failed
    last_error: str = Column(String(500), nullable=True)  # Last error message
    sync_interval_hours: int = Column(Integer, default=6)  # How often to sync
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self) -> str:
        return f"<JobSource(name={self.name}, enabled={self.is_enabled}, configured={self.is_configured})>"
