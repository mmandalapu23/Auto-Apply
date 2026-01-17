"""Admin-only endpoints for system management."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.db.models import User
from app.utils.rbac import require_admin
from app.db.session import SessionLocal
from passlib.context import CryptContext

router = APIRouter(prefix="/admin", tags=["admin"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCreateRequest(BaseModel):
    """Request to create a new user."""
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: str = "user"  # "user" or "admin"


class UserResponse(BaseModel):
    """User response model."""
    id: int
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True


@router.post("/users", response_model=UserResponse)
async def create_user(
    request: UserCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new user (admin only).
    
    Admin can create other users with specified role.
    """
    require_admin(current_user)
    
    # Check if user already exists
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create new user
    user = User(
        email=request.email,
        full_name=request.full_name,
        role=request.role if request.role in ["user", "admin"] else "user",
        hashed_password=pwd_context.hash(request.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return UserResponse.from_orm(user)


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    active_only: bool = True
):
    """
    List all users (admin only).
    """
    require_admin(current_user)
    
    query = db.query(User)
    if active_only:
        query = query.filter(User.is_active == True)
    
    users = query.all()
    return [UserResponse.from_orm(u) for u in users]


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user role or status (admin only).
    
    Admins can:
    - Change a user's role
    - Activate/deactivate users
    """
    require_admin(current_user)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if role and role in ["user", "admin"]:
        user.role = role
    
    if is_active is not None:
        user.is_active = is_active
    
    db.commit()
    db.refresh(user)
    return UserResponse.from_orm(user)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate a user (admin only).
    
    Note: We deactivate rather than delete to preserve audit trail.
    """
    require_admin(current_user)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent admin from deactivating themselves
    if user.id == current_user["user_id"]:
        raise HTTPException(
            status_code=400,
            detail="Cannot deactivate your own account"
        )
    
    user.is_active = False
    db.commit()
    
    return {"message": f"User {user.email} deactivated"}


@router.post("/jobs/sync")
async def trigger_job_sync(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger a full job sync across all enabled sources (admin only).
    
    This fetches latest jobs from all configured sources and marks inactive jobs as closed.
    """
    require_admin(current_user)
    
    from app.services.multi_source_job_service import MultiSourceJobService
    
    try:
        results = await MultiSourceJobService.sync_all_sources(
            db,
            user_id=current_user["user_id"],
            force=True,
        )
        
        return {
            "message": "Job sync completed",
            "timestamp": results["timestamp"].isoformat(),
            "total_sources": results["total_sources"],
            "synced_sources": results["synced_sources"],
            "failed_sources": results["failed_sources"],
            "total_jobs_imported": results["total_jobs_imported"],
            "details": results["details"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class JobSourceUpdate(BaseModel):
    """Request to update job source configuration."""
    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    is_enabled: Optional[bool] = None


class JobSourceResponse(BaseModel):
    """Job source response model."""
    id: int
    name: str
    display_name: str
    is_enabled: bool
    is_configured: bool
    last_sync_at: Optional[str] = None
    last_sync_status: str
    last_error: Optional[str] = None
    
    class Config:
        from_attributes = True


@router.get("/job-sources", response_model=List[JobSourceResponse])
async def list_job_sources(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get status of all job sources (admin only).
    
    Shows configuration status, last sync time, and any errors.
    """
    require_admin(current_user)
    
    from app.services.multi_source_job_service import MultiSourceJobService
    
    sources = MultiSourceJobService.get_source_status(db)
    return sources


@router.put("/job-sources/{source_id}", response_model=JobSourceResponse)
async def update_job_source(
    source_id: int,
    request: JobSourceUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update job source configuration (admin only).
    
    Can set API credentials and enable/disable sources.
    """
    require_admin(current_user)
    
    from app.services.multi_source_job_service import MultiSourceJobService
    
    try:
        source = MultiSourceJobService.update_source_config(
            db,
            source_id=source_id,
            api_key=request.api_key,
            api_endpoint=request.api_endpoint,
            is_enabled=request.is_enabled,
        )
        
        return JobSourceResponse.from_orm(source)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
