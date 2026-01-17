"""Multi-source job fetching and synchronization service."""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.db.models import Job, JobSource
from app.services.job_source_service import JobSourceService
from app.services.wellfound_service import WellfoundService
from app.services.flexjobs_service import FlexJobsService
from app.services.workday_service import WorkdayService


class MultiSourceJobService:
    """Manage job imports from multiple sources (Greenhouse, Wellfound, FlexJobs, Workday)."""

    SOURCE_SERVICES = {
        "greenhouse": JobSourceService,
        "wellfound": WellfoundService,
        "flexjobs": FlexJobsService,
        "workday": WorkdayService,
    }

    @classmethod
    async def sync_all_sources(
        cls,
        db: Session,
        user_id: int,
        force: bool = False,
    ) -> Dict:
        """
        Synchronize jobs from all enabled sources.
        
        Args:
            db: Database session
            user_id: Admin user triggering the sync
            force: Force sync even if interval not reached
        
        Returns:
            Summary dict with sync results
        """
        sources = db.query(JobSource).filter(JobSource.is_enabled == True).all()
        results = {
            "timestamp": datetime.utcnow(),
            "total_sources": len(sources),
            "synced_sources": 0,
            "failed_sources": 0,
            "total_jobs_imported": 0,
            "details": {},
        }
        
        for source in sources:
            # Check sync interval
            if not force and source.last_sync_at:
                interval = timedelta(hours=source.sync_interval_hours)
                if datetime.utcnow() - source.last_sync_at < interval:
                    results["details"][source.name] = {
                        "skipped": True,
                        "reason": "Sync interval not reached",
                    }
                    continue
            
            try:
                # Sync this source
                imported_count = await cls._sync_source(db, user_id, source)
                
                # Update source status
                source.last_sync_at = datetime.utcnow()
                source.last_sync_status = "success"
                source.last_error = None
                db.commit()
                
                results["synced_sources"] += 1
                results["total_jobs_imported"] += imported_count
                results["details"][source.name] = {
                    "status": "success",
                    "jobs_imported": imported_count,
                }
            
            except Exception as e:
                # Record error
                source.last_sync_status = "failed"
                source.last_error = str(e)
                db.commit()
                
                results["failed_sources"] += 1
                results["details"][source.name] = {
                    "status": "failed",
                    "error": str(e),
                }
        
        return results

    @classmethod
    async def _sync_source(
        cls,
        db: Session,
        user_id: int,
        source: JobSource,
    ) -> int:
        """Synchronize a single job source."""
        if source.name == "greenhouse":
            return await JobSourceService.fetch_and_import_greenhouse(db, user_id)
        
        elif source.name == "wellfound":
            jobs = await WellfoundService.fetch_jobs(limit=50)
            return await cls._import_jobs(db, user_id, jobs, "wellfound")
        
        elif source.name == "flexjobs":
            if not source.api_key:
                raise ValueError("FlexJobs API key not configured")
            jobs = await FlexJobsService.fetch_jobs(source.api_key, limit=50)
            return await cls._import_jobs(db, user_id, jobs, "flexjobs")
        
        elif source.name == "workday":
            if not source.api_endpoint:
                raise ValueError("Workday domain not configured")
            jobs = await WorkdayService.fetch_jobs(source.api_endpoint, limit=50)
            return await cls._import_jobs(db, user_id, jobs, "workday")
        
        else:
            raise ValueError(f"Unknown source: {source.name}")

    @staticmethod
    async def _import_jobs(
        db: Session,
        user_id: int,
        jobs: List[Dict],
        source: str,
    ) -> int:
        """Import job dicts into database."""
        imported_count = 0
        
        for job_data in jobs:
            # Check if job already exists
            existing = db.query(Job).filter(
                Job.source == source,
                Job.source_job_id == job_data.get("source_job_id"),
            ).first()
            
            if existing:
                # Update existing job
                existing.last_synced_at = datetime.utcnow()
                existing.is_active = True
                continue
            
            # Create new job
            job = Job(
                user_id=user_id,
                title=job_data.get("title", "Untitled"),
                company=job_data.get("company", "Unknown"),
                url=job_data.get("url"),
                raw_jd=job_data.get("raw_jd", ""),
                location=job_data.get("location"),
                country=job_data.get("country"),
                is_remote=job_data.get("is_remote", False),
                employment_type=job_data.get("employment_type", "Unknown"),
                salary_range=job_data.get("salary_range"),
                source=source,
                source_job_id=job_data.get("source_job_id"),
                posting_date=job_data.get("posting_date"),
                last_synced_at=datetime.utcnow(),
                is_active=True,
            )
            
            # Categorize role
            job.role_category = JobSourceService._categorize_role(
                job.title,
                job.raw_jd,
            )
            
            db.add(job)
            imported_count += 1
        
        db.commit()
        return imported_count

    @staticmethod
    def get_source_status(db: Session) -> List[Dict]:
        """Get status of all job sources."""
        sources = db.query(JobSource).all()
        return [
            {
                "id": s.id,
                "name": s.name,
                "display_name": s.display_name,
                "is_enabled": s.is_enabled,
                "is_configured": s.is_configured,
                "last_sync_at": s.last_sync_at.isoformat() if s.last_sync_at else None,
                "last_sync_status": s.last_sync_status,
                "last_error": s.last_error,
            }
            for s in sources
        ]

    @staticmethod
    def update_source_config(
        db: Session,
        source_id: int,
        api_key: Optional[str] = None,
        api_endpoint: Optional[str] = None,
        is_enabled: Optional[bool] = None,
    ) -> JobSource:
        """Update job source configuration (admin only)."""
        source = db.query(JobSource).filter(JobSource.id == source_id).first()
        if not source:
            raise ValueError(f"Job source {source_id} not found")
        
        if api_key:
            source.api_key = api_key
            source.is_configured = True
        
        if api_endpoint:
            source.api_endpoint = api_endpoint
            source.is_configured = True
        
        if is_enabled is not None:
            source.is_enabled = is_enabled
        
        db.commit()
        db.refresh(source)
        return source
