"""Server-rendered views for quick UI access."""
from pathlib import Path
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.job_service import JobService

router = APIRouter()

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@router.get("/")
async def home(request: Request):
    # Redirect root to jobs list for MVP
    return RedirectResponse(url="/jobs")


@router.get("/jobs")
async def jobs_page(request: Request, db: Session = Depends(get_db)):
    # For MVP, show jobs for user_id=1; adjust when auth wiring is ready
    jobs = JobService.list_jobs(db, user_id=1, limit=50)
    print(f"DEBUG: Found {len(jobs)} jobs for user_id=1")
    for job in jobs:
        print(f"  - Job: id={job.id}, title={job.title}")
    return templates.TemplateResponse("jobs.html", {"request": request, "jobs": jobs})


@router.get("/jobs/{job_id}")
async def job_detail(request: Request, job_id: int, db: Session = Depends(get_db)):
    try:
        job = JobService.get_job(db, job_id, user_id=1)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return templates.TemplateResponse("job_detail.html", {"request": request, "job": job})
