"""Main API router."""
from fastapi import APIRouter
from app.api.routers import auth, profile, jobs, resumes, applications, frontend

router = APIRouter(prefix="/api/v1")

# Include module-specific routers
router.include_router(auth.router)
router.include_router(profile.router)
router.include_router(jobs.router)
router.include_router(resumes.router)
router.include_router(applications.router)
router.include_router(frontend.router)
