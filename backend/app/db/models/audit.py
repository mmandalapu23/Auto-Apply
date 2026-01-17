"""Audit log models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from app.db.base import Base


class AuditLog(Base):
    """Append-only audit log for all sensitive operations."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    action = Column(String, nullable=False)  # e.g., "resume_generated", "jd_extracted", "application_queued"
    resource_type = Column(String, nullable=False)  # e.g., "resume", "job", "application"
    resource_id = Column(Integer, nullable=True)  # ID of the resource
    
    # Detailed info (JSON)
    details = Column(Text, nullable=True)
    
    # For resume generation: which JD, which profile version
    context = Column("metadata", Text, nullable=True)  # JSON with additional context stored in DB column "metadata"
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
