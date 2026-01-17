"""Profile endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.profile import ProfileSchema, ProfileUpdateRequest
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileSchema)
async def get_profile(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user profile."""
    try:
        profile = ProfileService.get_profile(db, current_user["user_id"])
        return ProfileService.profile_to_schema(profile)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("", response_model=ProfileSchema)
async def update_profile(
    request: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile."""
    try:
        profile = ProfileService.update_profile(db, current_user["user_id"], request)
        return ProfileService.profile_to_schema(profile)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
