"""Application models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class ApplicationStatus(str, enum.Enum):
    """Application status."""
    PENDING = "pending"  # Waiting to be generated
    READY_FOR_REVIEW = "ready_for_review"  # Resume generated, waiting user approval
    SUBMITTED = "submitted"  # User approved
    COMPLETED = "completed"  # Application processed


class Application(Base):
    """Job application record."""
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.PENDING, nullable=False)
    
    # Matching score
    match_score = Column(String, nullable=True)  # JSON: {"overall": 0.85, "skills": 0.9, ...}
    
    # Missing requirements
    missing_requirements = Column(Text, nullable=True)  # JSON: [{"type": "skill", "name": "..."}, ...]
    
    # Scheduled application (if scheduled via scheduler)
    scheduled_for = Column(DateTime, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
