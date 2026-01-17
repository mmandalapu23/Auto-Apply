"""Web routes for server-rendered UI pages."""
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.job_service import JobService

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@router.get("/")
async def home():
    """Redirect to jobs page."""
    return RedirectResponse(url="/jobs")


@router.get("/jobs")
async def jobs_page(request: Request, db: Session = Depends(get_db)):
    """Display all job listings."""
    jobs = JobService.list_jobs(db, user_id=1, limit=50)
    return templates.TemplateResponse("jobs.html", {"request": request, "jobs": jobs})


@router.get("/jobs/{job_id}")
async def job_detail(request: Request, job_id: int, db: Session = Depends(get_db)):
    """Display job details page."""
    try:
        job = JobService.get_job(db, job_id, user_id=1)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return templates.TemplateResponse("job_detail.html", {"request": request, "job": job})
