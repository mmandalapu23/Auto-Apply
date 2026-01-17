"""Job service for managing job postings."""
from datetime import datetime
import json
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

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
    def list_jobs(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        role_category: Optional[str] = None,
        country: Optional[str] = None,
        employment_type: Optional[str] = None,
        is_active_only: bool = True,
    ) -> List[Job]:
        """List all jobs for a user with optional filters."""
        query = db.query(Job).filter(Job.user_id == user_id)
        
        if is_active_only:
            query = query.filter(Job.is_active == True)
        
        if role_category:
            query = query.filter(Job.role_category == role_category)
        
        if country:
            query = query.filter(Job.country == country)
        
        if employment_type:
            query = query.filter(Job.employment_type == employment_type)
        
        return query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()

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
    ) -> Tuple[List[Job], int, int]:
        """
        Import jobs from a Greenhouse board with comprehensive data.

        Args:
            db: Database session
            user_id: User to associate jobs with
            request: Import configuration

        Returns:
            Tuple of (created jobs, updated jobs count, skipped count)
        """
        fetched = await JobSourceService.fetch_greenhouse_jobs(
            board_token=request.board_token,
            company=request.company,
            limit=request.limit,
            include_keywords=request.include_keywords,
        )

        created: List[Job] = []
        updated = 0
        skipped = 0
        now = datetime.utcnow()

        for payload in fetched:
            source_job_id = payload.get("source_job_id")
            url = payload.get("url")

            # Check for existing job by source_job_id or URL
            existing = None
            if source_job_id:
                existing = db.query(Job).filter(
                    Job.user_id == user_id,
                    Job.source == "greenhouse",
                    Job.source_job_id == source_job_id,
                ).first()
            
            if not existing and url and request.dedupe:
                existing = db.query(Job).filter(
                    Job.user_id == user_id,
                    Job.url == url,
                ).first()

            if existing:
                # Update existing job with latest data
                existing.title = payload.get("title") or existing.title
                existing.location = payload.get("location")
                existing.country = payload.get("country")
                existing.is_remote = payload.get("is_remote", False)
                existing.employment_type = payload.get("employment_type")
                existing.salary_range = payload.get("salary_range")
                existing.responsibilities = payload.get("responsibilities")
                existing.required_skills = payload.get("required_skills")
                existing.preferred_skills = payload.get("preferred_skills")
                existing.role_category = payload.get("role_category")
                existing.is_active = True  # Reactivate if it was marked inactive
                existing.last_synced_at = now
                updated += 1
            else:
                # Create new job with comprehensive data
                job = Job(
                    user_id=user_id,
                    title=payload.get("title") or "Untitled",
                    company=payload.get("company") or request.board_token,
                    url=url,
                    raw_jd=payload.get("raw_jd") or "",
                    location=payload.get("location"),
                    country=payload.get("country"),
                    is_remote=payload.get("is_remote", False),
                    employment_type=payload.get("employment_type"),
                    salary_range=payload.get("salary_range"),
                    responsibilities=payload.get("responsibilities"),
                    required_skills=payload.get("required_skills"),
                    preferred_skills=payload.get("preferred_skills"),
                    source="greenhouse",
                    source_job_id=source_job_id,
                    posting_date=payload.get("posting_date"),
                    role_category=payload.get("role_category"),
                    is_active=True,
                    last_synced_at=now,
                )
                db.add(job)
                created.append(job)

        db.commit()
        for job in created:
            db.refresh(job)

        return created, updated, skipped

    @staticmethod
    async def sync_jobs(
        db: Session,
        user_id: int,
        source: str = "greenhouse",
        board_token: Optional[str] = None,
    ) -> Tuple[int, int, int]:
        """
        Sync jobs with external source and mark inactive jobs.

        Args:
            db: Database session
            user_id: User ID
            source: Job source (greenhouse, etc.)
            board_token: Source board identifier

        Returns:
            Tuple of (new_count, updated_count, marked_inactive_count)
        """
        if source != "greenhouse" or not board_token:
            return 0, 0, 0

        # Fetch current jobs from source
        current_jobs = await JobSourceService.fetch_greenhouse_jobs(
            board_token=board_token,
            limit=1000,  # Fetch all
        )

        # Get source job IDs that are currently active
        active_source_ids = {job.get("source_job_id") for job in current_jobs if job.get("source_job_id")}

        # Import/update jobs
        request = JobImportRequest(
            source=source,
            board_token=board_token,
            limit=1000,
            dedupe=True,
        )
        created, updated, _ = await JobService.import_from_greenhouse(db, user_id, request)

        # Mark jobs as inactive if they're no longer in the source
        our_jobs = db.query(Job).filter(
            Job.user_id == user_id,
            Job.source == source,
            Job.is_active == True,
        ).all()

        marked_inactive = 0
        for job in our_jobs:
            if job.source_job_id and job.source_job_id not in active_source_ids:
                job.is_active = False
                job.last_synced_at = datetime.utcnow()
                marked_inactive += 1

        db.commit()
        return len(created), updated, marked_inactive

    # Aliases for backward compatibility
    create_job = create
    get_job = get_by_id
    job_to_schema = to_schema
    job_to_detail_schema = to_detail_schema
    import_jobs_from_greenhouse = import_from_greenhouse
