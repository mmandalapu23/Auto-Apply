"""API routers."""
from fastapi import APIRouter
from app.api.routers import auth, profile, jobs, resumes, applications

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(profile.router)
api_router.include_router(jobs.router)
api_router.include_router(resumes.router)
api_router.include_router(applications.router)

__all__ = ["api_router"]
