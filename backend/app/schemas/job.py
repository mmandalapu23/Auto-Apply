"""Job schemas."""
from pydantic import BaseModel, HttpUrl
from typing import Optional, Literal
from datetime import datetime


class JobCreateRequest(BaseModel):
    """Create job request."""
    title: str
    company: str
    url: Optional[HttpUrl] = None
    raw_jd: str  # Pasted job description


class JobImportRequest(BaseModel):
    """Import jobs from an external source (e.g., Greenhouse)."""
    source: Literal["greenhouse"]
    board_token: str  # Greenhouse board token, e.g., "airbnb"
    company: Optional[str] = None  # Optional override for company name
    limit: int = 20  # Max jobs to ingest
    dedupe: bool = True  # Skip URLs already stored for the user
    include_keywords: list[str] = [  # Titles must contain one of these (case-insensitive)
        "data engineer",
        "data analyst",
        "software engineer",
        "software developer",
        "backend engineer",
        "full stack",
    ]


class JobSchema(BaseModel):
    """Job listing."""
    id: int
    user_id: int
    title: str
    company: str
    url: Optional[str] = None
    raw_jd: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class JobDetailSchema(JobSchema):
    """Job with extracted data and matching results."""
    extracted_data: Optional[dict] = None  # Parsed JD
    match_score: Optional[float] = None
    missing_requirements: Optional[list] = None
