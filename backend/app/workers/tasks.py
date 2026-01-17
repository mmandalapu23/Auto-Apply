"""Celery tasks."""
from celery import shared_task
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.resume_service import ResumeService
from app.services.document_service import DocumentService
from app.services.application_service import ApplicationService
from app.services.audit_service import AuditService
from app.llm.pipeline import LLMPipeline
import json


@shared_task
def generate_resume_task(resume_id: int, user_id: int):
    """Async task to generate resume."""
    try:
        db = SessionLocal()
        pipeline = LLMPipeline()
        
        resume = db.query(ResumeService).filter(ResumeService.id == resume_id).first()
        if not resume:
            return {"status": "error", "message": "Resume not found"}
        
        # Parse structured data
        structured = json.loads(resume.structured_data)
        
        # Render PDF
        html_content = DocumentService.render_resume_html(structured)
        pdf_path = DocumentService.render_resume_pdf(resume_id, html_content)
        
        # Update resume
        ResumeService.update_pdf_path(db, resume_id, pdf_path)
        
        AuditService.log_action(
            db, user_id, "resume_pdf_generated", "resume", resume_id,
            context={"pdf_path": pdf_path}
        )
        
        db.close()
        return {"status": "success", "pdf_path": pdf_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@shared_task
def queue_application_task(job_id: int, user_id: int):
    """Queue application for later submission."""
    try:
        db = SessionLocal()
        
        app = ApplicationService.create_application(db, user_id, job_id)
        
        AuditService.log_action(
            db, user_id, "application_queued", "application", app.id,
            context={"job_id": job_id}
        )
        
        db.close()
        return {"status": "success", "application_id": app.id}
    except Exception as e:
        return {"status": "error", "message": str(e)}
