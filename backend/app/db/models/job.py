"""Job and Job Description models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Job(Base):
    """Job posting."""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    url = Column(String, nullable=True)
    
    # Raw JD text
    raw_jd = Column(Text, nullable=False)
    
    # Extracted structured JD (JSON string)
    extracted_data = Column(Text, nullable=True)  # JSON: {"responsibilities": [...], "must_have_skills": [...], ...}
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resumes = relationship("Resume", back_populates="job")
