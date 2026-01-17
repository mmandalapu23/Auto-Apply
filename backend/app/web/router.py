"""Web routes for server-rendered UI pages."""
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Job
from app.services.job_service import JobService
from app.services.job_source_service import JobSourceService

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@router.get("/")
async def home():
    """Redirect to jobs page."""
    return RedirectResponse(url="/jobs")


@router.get("/jobs")
async def jobs_page(
    request: Request,
    db: Session = Depends(get_db),
    role: Optional[str] = None,
    country: Optional[str] = None,
):
    """Display all job listings with optional filters."""
    jobs = JobService.list_jobs(
        db,
        user_id=1,
        limit=100,
        role_category=role,
        country=country,
        is_active_only=True,
    )
    
    # Get available filter options
    all_jobs = db.query(Job).filter(Job.user_id == 1, Job.is_active == True).all()
    role_categories = sorted(set(j.role_category for j in all_jobs if j.role_category))
    countries = sorted(set(j.country for j in all_jobs if j.country))
    
    return templates.TemplateResponse(
        "jobs.html",
        {
            "request": request,
            "jobs": jobs,
            "role_categories": role_categories,
            "countries": countries,
            "selected_role": role,
            "selected_country": country,
        },
    )


@router.get("/jobs/{job_id}")
async def job_detail(request: Request, job_id: int, db: Session = Depends(get_db)):
    """Display job details page."""
    try:
        job = JobService.get_job(db, job_id, user_id=1)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return templates.TemplateResponse("job_detail.html", {"request": request, "job": job})


@router.post("/jobs/refresh")
async def refresh_jobs(request: Request, db: Session = Depends(get_db)):
    """Refresh jobs from all configured sources."""
    # Configure your job sources here
    sources = [
        {"board_token": "airbnb", "company": "Airbnb"},
        {"board_token": "stripe", "company": "Stripe"},
    ]
    
    total_new = 0
    total_updated = 0
    total_archived = 0
    
    for source in sources:
        new, updated, archived = await JobService.sync_jobs(
            db,
            user_id=1,
            source="greenhouse",
            board_token=source["board_token"],
        )
        total_new += new
        total_updated += updated
        total_archived += archived
    
    return RedirectResponse(
        url=f"/jobs?message=Refreshed: {total_new} new, {total_updated} updated, {total_archived} archived",
        status_code=303,
    )
