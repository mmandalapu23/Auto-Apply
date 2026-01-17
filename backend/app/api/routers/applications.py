"""Application endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.application import ApplicationCreateRequest, ApplicationStatusUpdateRequest
from app.services.application_service import ApplicationService
from app.services.dashboard_service import DashboardService
from app.services.audit_service import AuditService

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("")
async def create_application(
    request: ApplicationCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create application for job."""
    try:
        app = ApplicationService.create_application(db, current_user["user_id"], request.job_id)
        AuditService.log_action(
            db, current_user["user_id"], "application_created", "application", app.id,
            context={"job_id": request.job_id}
        )
        return {
            "id": app.id,
            "job_id": app.job_id,
            "status": app.status,
            "created_at": app.created_at
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
async def list_applications(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    status: str = None,
    skip: int = 0,
    limit: int = 50
):
    """List user's applications."""
    apps = ApplicationService.list_applications(db, current_user["user_id"], status, skip, limit)
    return [
        {
            "id": app.id,
            "job_id": app.job_id,
            "resume_id": app.resume_id,
            "status": app.status,
            "created_at": app.created_at
        }
        for app in apps
    ]


@router.get("/{app_id}")
async def get_application(
    app_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get application details."""
    try:
        app = ApplicationService.get_application(db, app_id, current_user["user_id"])
        return {
            "id": app.id,
            "job_id": app.job_id,
            "resume_id": app.resume_id,
            "status": app.status,
            "match_score": app.match_score,
            "missing_requirements": app.missing_requirements,
            "created_at": app.created_at
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{app_id}")
async def update_application_status(
    app_id: int,
    request: ApplicationStatusUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update application status."""
    try:
        app = ApplicationService.get_application(db, app_id, current_user["user_id"])
        app = ApplicationService.update_status(db, app_id, request.status)
        AuditService.log_action(
            db, current_user["user_id"], "application_status_updated", "application", app_id,
            context={"status": request.status}
        )
        return {
            "id": app.id,
            "status": app.status,
            "updated_at": app.updated_at
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Dashboard routes
dashboard_router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@dashboard_router.get("/metrics/daily")
async def get_daily_metrics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get today's job and application metrics."""
    return DashboardService.get_daily_metrics(db, current_user["user_id"])


@dashboard_router.get("/metrics/weekly")
async def get_weekly_metrics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get this week's metrics (last 7 days)."""
    return DashboardService.get_weekly_metrics(db, current_user["user_id"])


@dashboard_router.get("/metrics/monthly")
async def get_monthly_metrics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get this month's metrics."""
    return DashboardService.get_monthly_metrics(db, current_user["user_id"])


@dashboard_router.get("/trends/jobs")
async def get_job_trends(
    days: int = Query(30, ge=7, le=365),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get job posting trends over N days."""
    return DashboardService.get_job_trends(db, current_user["user_id"], days=days)


@dashboard_router.get("/distribution/roles")
async def get_role_distribution(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get distribution of jobs by role category."""
    return DashboardService.get_role_distribution(db, current_user["user_id"])


@dashboard_router.get("/stats/companies")
async def get_company_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get top 10 companies with most job openings."""
    return DashboardService.get_company_stats(db, current_user["user_id"])


@dashboard_router.get("/funnel")
async def get_application_funnel(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get application status funnel and completion metrics."""
    return DashboardService.get_application_funnel(db, current_user["user_id"])
