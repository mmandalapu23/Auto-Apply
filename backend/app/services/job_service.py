"""Job service."""
import json
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.db.models import Job
from app.schemas.job import JobCreateRequest, JobSchema, JobDetailSchema, JobImportRequest
from app.services.job_source_service import JobSourceService


class JobService:
    """Job management."""
    
    @staticmethod
    def create_job(db: Session, user_id: int, request: JobCreateRequest) -> Job:
        """Create job posting."""
        job = Job(
            user_id=user_id,
            title=request.title,
            company=request.company,
            url=str(request.url) if request.url else None,
            raw_jd=request.raw_jd
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job
    
    @staticmethod
    def get_job(db: Session, job_id: int, user_id: int) -> Job:
        """Get job by ID (user-scoped)."""
        job = db.query(Job).filter(
            Job.id == job_id,
            Job.user_id == user_id
        ).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")
        return job
    
    @staticmethod
    def list_jobs(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> list:
        """List user's jobs."""
        return db.query(Job).filter(
            Job.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_extracted_data(db: Session, job_id: int, extracted_data: dict) -> Job:
        """Store extracted JD data."""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        job.extracted_data = json.dumps(extracted_data)
        db.commit()
        db.refresh(job)
        return job
    
    @staticmethod
    def job_to_schema(job: Job) -> JobSchema:
        """Convert ORM to schema."""
        return JobSchema(
            id=job.id,
            user_id=job.user_id,
            title=job.title,
            company=job.company,
            url=job.url,
            raw_jd=job.raw_jd,
            created_at=job.created_at,
            updated_at=job.updated_at
        )
    
    @staticmethod
    def job_to_detail_schema(job: Job) -> JobDetailSchema:
        """Convert ORM to detail schema with extracted data."""
        extracted = None
        if job.extracted_data:
            try:
                extracted = json.loads(job.extracted_data)
            except:
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
            updated_at=job.updated_at
        )

    @staticmethod
    async def import_jobs_from_greenhouse(
        db: Session,
        user_id: int,
        request: JobImportRequest,
    ) -> Tuple[List[Job], int]:
        """Import jobs from a Greenhouse board and persist them.

        Returns:
            created_jobs: list of Job models created
            skipped: how many jobs were skipped due to dedupe
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
            if request.dedupe and url:
                existing = db.query(Job).filter(
                    Job.user_id == user_id,
                    Job.url == url,
                ).first()
                if existing:
                    skipped += 1
                    continue

            job = Job(
                user_id=user_id,
                title=payload.get("title") or "Untitled role",
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
