"""Resume endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.resume import GenerateResumeRequest
from app.services.resume_service import ResumeService
from app.services.job_service import JobService
from app.services.profile_service import ProfileService
from app.services.document_service import DocumentService
from app.services.audit_service import AuditService
from app.llm.pipeline import LLMPipeline
from app.llm.validators import validate_no_fabrication, validate_ats_formatting
import json

router = APIRouter(prefix="/resumes", tags=["resumes"])
llm_pipeline = LLMPipeline()


@router.post("")
async def generate_resume(
    request: GenerateResumeRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate tailored resume for job."""
    try:
        job = JobService.get_job(db, request.job_id, current_user["user_id"])
        profile = ProfileService.get_profile(db, current_user["user_id"])
        
        # Extract JD if needed
        if job.extracted_data:
            jd_dict = json.loads(job.extracted_data)
            from app.schemas.jd import JDStructuredSchema
            jd_structured = JDStructuredSchema(**jd_dict)
        else:
            jd_structured = await llm_pipeline.extract_jd(job.raw_jd)
            JobService.update_extracted_data(db, request.job_id, jd_structured.model_dump())
        
        # Map evidence
        evidence_map = await llm_pipeline.map_evidence(profile, jd_structured)
        
        # Generate resume
        resume_structured = await llm_pipeline.generate_resume(profile, jd_structured, evidence_map)
        
        # Validate
        passed, issues = await llm_pipeline.validate_resume(resume_structured)
        validation_result = {"passed": passed, "issues": issues}
        
        # Render ATS text
        ats_text = DocumentService.render_resume_ats_text(resume_structured)
        
        # Save to DB
        resume = ResumeService.create_resume(
            db, current_user["user_id"], request.job_id,
            resume_structured, ats_text
        )
        ResumeService.update_validation(db, resume.id, validation_result)
        
        # Audit
        AuditService.log_action(
            db, current_user["user_id"], "resume_generated", "resume", resume.id,
            context={"job_id": request.job_id, "validation_passed": passed}
        )
        
        # Render PDF (for MVP, save as HTML)
        html_content = DocumentService.render_resume_html(resume_structured)
        pdf_path = await DocumentService.render_resume_pdf(resume.id, html_content)
        ResumeService.update_pdf_path(db, resume.id, pdf_path)
        
        return {
            "resume_id": resume.id,
            "structured_data": resume_structured,
            "ats_text": ats_text,
            "validation": validation_result,
            "pdf_path": pdf_path
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{resume_id}")
async def get_resume(
    resume_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get resume details."""
    try:
        resume = ResumeService.get_resume(db, resume_id, current_user["user_id"])
        return {
            "id": resume.id,
            "job_id": resume.job_id,
            "structured_data": json.loads(resume.structured_data),
            "ats_text": resume.ats_text,
            "validation_passed": resume.validation_passed,
            "pdf_path": resume.pdf_path,
            "created_at": resume.created_at
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{resume_id}/pdf")
async def get_resume_pdf(
    resume_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get resume PDF export."""
    try:
        resume = ResumeService.get_resume(db, resume_id, current_user["user_id"])
        if not resume.pdf_path:
            raise ValueError("PDF not generated yet")
        return {"pdf_path": resume.pdf_path}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
