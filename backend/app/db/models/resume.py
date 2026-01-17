"""Resume models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base


class Resume(Base):
    """Generated resume version."""
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    
    # Structured resume data (JSON)
    # Contains: summary, skills, experience[], projects[], education[]
    # Each bullet includes evidence_refs: [{"type": "experience", "id": 123, "bullet_idx": 0}, ...]
    structured_data = Column(Text, nullable=False)  # JSON
    
    # ATS plain text version
    ats_text = Column(Text, nullable=False)
    
    # Validation results
    validation_passed = Column(JSON, nullable=True)  # {"passed": bool, "issues": [...]}
    
    # PDF file path (relative to /storage)
    pdf_path = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job = relationship("Job", back_populates="resumes")


class ResumeBullet(Base):
    """Individual resume bullet with evidence mapping (for future enhancements)."""
    __tablename__ = "resume_bullets"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    section = Column(String, nullable=False)  # "experience", "projects", "skills"
    text = Column(Text, nullable=False)
    
    # Evidence references (JSON): [{"type": "experience", "id": 123, "bullet_idx": 0}, ...]
    evidence_refs = Column(JSON, nullable=True)
    
    needs_user_input = Column(String, nullable=True)  # Reason if NEEDS_USER_INPUT
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
