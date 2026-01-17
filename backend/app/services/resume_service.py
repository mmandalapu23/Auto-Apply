"""Resume service."""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import Resume
from app.schemas.resume import ResumeStructuredSchema


class ResumeService:
    """Encapsulates resume CRUD helpers."""

    @staticmethod
    def create(
        db: Session,
        user_id: int,
        job_id: int,
        structured: ResumeStructuredSchema,
        ats_text: str,
    ) -> Resume:
        """Persist a generated resume."""

        resume = Resume(
            user_id=user_id,
            job_id=job_id,
            structured_data=structured.model_dump_json(),
            ats_text=ats_text,
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume

    @staticmethod
    def get(db: Session, resume_id: int, user_id: int) -> Resume:
        """Fetch a resume for a user or raise if missing."""

        resume = (
            db.query(Resume)
            .filter(Resume.id == resume_id, Resume.user_id == user_id)
            .first()
        )
        if not resume:
            raise ValueError(f"Resume {resume_id} not found")
        return resume

    @staticmethod
    def latest_for_job(db: Session, job_id: int, user_id: int) -> Optional[Resume]:
        """Return the newest resume for a job if one exists."""

        return (
            db.query(Resume)
            .filter(Resume.job_id == job_id, Resume.user_id == user_id)
            .order_by(Resume.created_at.desc())
            .first()
        )

    @staticmethod
    def update_pdf_path(db: Session, resume_id: int, pdf_path: str) -> Resume:
        """Store the file path for the rendered PDF."""

        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ValueError(f"Resume {resume_id} not found")

        resume.pdf_path = pdf_path
        db.commit()
        db.refresh(resume)
        return resume

    @staticmethod
    def update_validation(db: Session, resume_id: int, is_valid: bool) -> Resume:
        """Persist the validation result flag."""

        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise ValueError(f"Resume {resume_id} not found")

        resume.validation_passed = is_valid
        db.commit()
        db.refresh(resume)
        return resume

    @staticmethod
    def to_schema(resume: Resume):
        """Hydrate a pydantic schema from the ORM entity."""

        structured = None
        if resume.structured_data:
            structured = ResumeStructuredSchema.model_validate_json(resume.structured_data)

        return {
            "id": resume.id,
            "user_id": resume.user_id,
            "job_id": resume.job_id,
            "pdf_path": resume.pdf_path,
            "ats_text": resume.ats_text,
            "validation_passed": resume.validation_passed,
            "structured_data": structured,
            "created_at": resume.created_at,
            "updated_at": resume.updated_at,
        }

    # Backwards compatible aliases
    create_resume = create
    get_resume = get
    get_resume_by_job = latest_for_job
