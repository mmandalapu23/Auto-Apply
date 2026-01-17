"""Job endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.job import JobCreateRequest, JobSchema, JobDetailSchema, JobImportRequest
from app.schemas.jd import JDExtractRequest, JDStructuredSchema, EvidenceMapSchema
from app.services.job_service import JobService
from app.services.profile_service import ProfileService
from app.llm.pipeline import LLMPipeline
from app.services.audit_service import AuditService
import json

router = APIRouter(prefix="/jobs", tags=["jobs"])
llm_pipeline = LLMPipeline()


@router.post("", response_model=JobSchema)
async def create_job(
    request: JobCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create job posting."""
    try:
        job = JobService.create_job(db, current_user["user_id"], request)
        AuditService.log_action(
            db, current_user["user_id"], "job_created", "job", job.id,
            details={"title": job.title, "company": job.company}
        )
        return JobService.job_to_schema(job)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/import")
async def import_jobs(
    request: JobImportRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Import jobs from external sources (e.g., Greenhouse)."""
    if request.source != "greenhouse":
        raise HTTPException(status_code=400, detail="Unsupported source")

    try:
        created_jobs, skipped = await JobService.import_jobs_from_greenhouse(
            db, current_user["user_id"], request
        )

        for job in created_jobs:
            AuditService.log_action(
                db,
                current_user["user_id"],
                "job_imported",
                "job",
                job.id,
                details={"source": request.source, "title": job.title, "company": job.company},
                context={"url": job.url},
            )

        return {
            "source": request.source,
            "created_count": len(created_jobs),
            "skipped": skipped,
            "jobs": [JobService.job_to_schema(j) for j in created_jobs],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list)
async def list_jobs(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """List user's jobs."""
    jobs = JobService.list_jobs(db, current_user["user_id"], skip, limit)
    return [JobService.job_to_schema(j) for j in jobs]


@router.get("/{job_id}", response_model=JobDetailSchema)
async def get_job(
    job_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get job details."""
    try:
        job = JobService.get_job(db, job_id, current_user["user_id"])
        return JobService.job_to_detail_schema(job)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{job_id}/extract")
async def extract_jd(
    job_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Extract and structure JD."""
    try:
        job = JobService.get_job(db, job_id, current_user["user_id"])
        jd_structured = await llm_pipeline.extract_jd(job.raw_jd)
        JobService.update_extracted_data(db, job_id, jd_structured.model_dump())
        AuditService.log_action(
            db, current_user["user_id"], "jd_extracted", "job", job_id
        )
        return jd_structured
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{job_id}/match")
async def match_job(
    job_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Match job to user profile and get match score."""
    try:
        job = JobService.get_job(db, job_id, current_user["user_id"])
        profile = ProfileService.get_profile(db, current_user["user_id"])
        
        # Extract JD if not already done
        if not job.extracted_data:
            jd_structured = await llm_pipeline.extract_jd(job.raw_jd)
            JobService.update_extracted_data(db, job_id, jd_structured.model_dump())
        else:
            jd_dict = json.loads(job.extracted_data)
            jd_structured = JDStructuredSchema(**jd_dict)
        
        # Map evidence
        evidence_map = await llm_pipeline.map_evidence(profile, jd_structured)
        
        # Calculate match score
        from app.services.matching_service import MatchingService
        match_score = MatchingService.calculate_match_score(evidence_map)
        
        AuditService.log_action(
            db, current_user["user_id"], "job_matched", "job", job_id,
            context={"overall_score": match_score.overall_score}
        )
        
        return {
            "job_id": job_id,
            "match_score": match_score,
            "evidence_map": evidence_map
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
