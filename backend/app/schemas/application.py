"""Application and scheduling schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ApplicationSchema(BaseModel):
    """Application record."""
    id: int
    user_id: int
    job_id: int
    resume_id: Optional[int] = None
    status: str
    match_score: Optional[dict] = None
    missing_requirements: Optional[list] = None
    scheduled_for: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ApplicationCreateRequest(BaseModel):
    """Create application request."""
    job_id: int


class ApplicationStatusUpdateRequest(BaseModel):
    """Update application status."""
    status: str


class ScheduleSettingsRequest(BaseModel):
    """Schedule settings for daily applications."""
    target_applications_per_day: int
    time_window_start: str  # HH:MM
    time_window_end: str  # HH:MM
    enabled: bool = True
