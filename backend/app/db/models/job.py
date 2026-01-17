"""Job and Job Description models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base


class Job(Base):
    """Job posting with comprehensive tracking and sync metadata."""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic job info
    title = Column(String, nullable=False, index=True)
    company = Column(String, nullable=False, index=True)
    url = Column(String, nullable=True)
    
    # Location and remote status
    location = Column(String, nullable=True)  # City, State/Country
    country = Column(String, nullable=True, index=True)  # USA, India, UK, etc.
    is_remote = Column(Boolean, default=False)
    
    # Employment details
    employment_type = Column(String, nullable=True)  # Full-time, Part-time, Contract, Internship
    salary_range = Column(String, nullable=True)  # e.g., "$100k-$150k", "Competitive"
    
    # Job description
    raw_jd = Column(Text, nullable=False)
    responsibilities = Column(Text, nullable=True)  # Extracted responsibilities section
    required_skills = Column(Text, nullable=True)  # JSON array
    preferred_skills = Column(Text, nullable=True)  # JSON array
    
    # Extracted structured JD (JSON string)
    extracted_data = Column(Text, nullable=True)  # Full structured extraction
    
    # Source tracking for sync and deduplication
    source = Column(String, nullable=True, index=True)  # greenhouse, linkedin, indeed, etc.
    source_job_id = Column(String, nullable=True, index=True)  # External job ID from source
    posting_date = Column(DateTime, nullable=True)
    
    # Sync and status tracking
    is_active = Column(Boolean, default=True, index=True)  # False = closed/archived
    last_synced_at = Column(DateTime, nullable=True)  # Last time we checked if job still exists
    
    # Role categorization for filtering
    role_category = Column(String, nullable=True, index=True)  # Data Engineer, Data Analyst, Software Developer, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resumes = relationship("Resume", back_populates="job")
