"""Resume service."""
import json
from sqlalchemy.orm import Session
from app.db.models import Resume
from app.schemas.resume import ResumeStructuredSchema


class ResumeService:
    """Resume management."""
    
    @staticmethod
    def create_resume(
        db: Session,
        user_id: int,
        job_id: int,
        structured_data: ResumeStructuredSchema,
        ats_text: str
    ) -> Resume:
        """Create resume record."""
        resume = Resume(
            user_id=user_id,
            job_id=job_id,
            structured_data=structured_data.model_dump_json(),
            ats_text=ats_text,
            validation_passed=None,
            pdf_path=None
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume
    
    @staticmethod
    def get_resume(db: Session, resume_id: int, user_id: int) -> Resume:
        """Get resume (user-scoped)."""
        resume = db.query(Resume).filter(
            Resume.id == resume_id,
            Resume.user_id == user_id
        ).first()
        if not resume:
            raise ValueError(f"Resume {resume_id} not found")
        return resume
    
    @staticmethod
    def get_resume_by_job(db: Session, job_id: int, user_id: int) -> Resume:
        """Get latest resume for a job."""
        resume = db.query(Resume).filter(
            Resume.job_id == job_id,
            Resume.user_id == user_id
        ).order_by(Resume.created_at.desc()).first()
        return resume
    
    @staticmethod
    def update_pdf_path(db: Session, resume_id: int, pdf_path: str) -> Resume:
        """Update PDF export path."""
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ValueError(f"Resume {resume_id} not found")
        
        resume.pdf_path = pdf_path
        db.commit()
        db.refresh(resume)
        return resume
    
    @staticmethod
    def update_validation(db: Session, resume_id: int, validation_result: dict) -> Resume:
        """Update validation results."""
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ValueError(f"Resume {resume_id} not found")
        
        resume.validation_passed = validation_result
        db.commit()
        db.refresh(resume)
        return resume
