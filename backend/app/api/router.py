"""API router aggregating all endpoint modules."""
from fastapi import APIRouter

from app.api.routers import admin, applications, auth, frontend, jobs, profile, resumes

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(admin.router)
router.include_router(profile.router)
router.include_router(jobs.router)
router.include_router(resumes.router)
router.include_router(applications.router)
router.include_router(applications.dashboard_router)
router.include_router(frontend.router)
