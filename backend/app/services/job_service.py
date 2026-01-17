"""Job service for managing job postings."""
import json
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.db.models import Job
from app.schemas.job import JobCreateRequest, JobDetailSchema, JobImportRequest, JobSchema
from app.services.job_source_service import JobSourceService


class JobService:
    """Handles job posting CRUD operations and imports."""

    @staticmethod
    def create(db: Session, user_id: int, data: JobCreateRequest) -> Job:
        """Create a new job posting."""
        job = Job(
            user_id=user_id,
            title=data.title,
            company=data.company,
            url=str(data.url) if data.url else None,
            raw_jd=data.raw_jd,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def get_by_id(db: Session, job_id: int, user_id: int) -> Job:
        """Retrieve a job by ID for a specific user."""
        job = db.query(Job).filter(Job.id == job_id, Job.user_id == user_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")
        return job

    @staticmethod
    def list_jobs(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List[Job]:
        """List all jobs for a user with pagination."""
        return (
            db.query(Job)
            .filter(Job.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_extracted_data(db: Session, job_id: int, extracted_data: dict) -> Job:
        """Store parsed job description data."""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")

        job.extracted_data = json.dumps(extracted_data)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def to_schema(job: Job) -> JobSchema:
        """Convert Job model to response schema."""
        return JobSchema(
            id=job.id,
            user_id=job.user_id,
            title=job.title,
            company=job.company,
            url=job.url,
            raw_jd=job.raw_jd,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )

    @staticmethod
    def to_detail_schema(job: Job) -> JobDetailSchema:
        """Convert Job model to detailed response schema."""
        extracted = None
        if job.extracted_data:
            try:
                extracted = json.loads(job.extracted_data)
            except json.JSONDecodeError:
                pass

        return JobDetailSchema(
            id=job.id,
            user_id=job.user_id,
            title=job.title,
            company=job.company,
            url=job.url,
            raw_jd=job.raw_jd,
            extracted_data=extracted,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )

    @staticmethod
    async def import_from_greenhouse(
        db: Session,
        user_id: int,
        request: JobImportRequest,
    ) -> Tuple[List[Job], int]:
        """
        Import jobs from a Greenhouse board.

        Args:
            db: Database session
            user_id: User to associate jobs with
            request: Import configuration

        Returns:
            Tuple of (created jobs, skipped count)
        """
        fetched = await JobSourceService.fetch_greenhouse_jobs(
            board_token=request.board_token,
            company=request.company,
            limit=request.limit,
            include_keywords=request.include_keywords,
        )

        created: List[Job] = []
        skipped = 0

        for payload in fetched:
            url = payload.get("url")

            # Deduplicate by URL if enabled
            if request.dedupe and url:
                exists = db.query(Job).filter(
                    Job.user_id == user_id,
                    Job.url == url,
                ).first()
                if exists:
                    skipped += 1
                    continue

            job = Job(
                user_id=user_id,
                title=payload.get("title") or "Untitled",
                company=payload.get("company") or request.board_token,
                url=url,
                raw_jd=payload.get("raw_jd") or "",
            )
            db.add(job)
            created.append(job)

        db.commit()
        for job in created:
            db.refresh(job)

        return created, skipped

    # Aliases for backward compatibility
    create_job = create
    get_job = get_by_id
    job_to_schema = to_schema
    job_to_detail_schema = to_detail_schema
    import_jobs_from_greenhouse = import_from_greenhouse
