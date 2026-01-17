"""JD extraction and processing schemas."""
from pydantic import BaseModel
from typing import List, Optional


class ResponsibilitySchema(BaseModel):
    """Extracted job responsibility."""
    text: str
    required: bool = True


class JDExtractRequest(BaseModel):
    """Request to extract JD."""
    raw_jd: str


class JDStructuredSchema(BaseModel):
    """Structured job description after extraction."""
    responsibilities: List[ResponsibilitySchema] = []
    must_have_skills: List[str] = []
    nice_to_have_skills: List[str] = []
    keywords: List[str] = []
    seniority_signals: List[str] = []
    years_experience: Optional[int] = None


class EvidenceRefSchema(BaseModel):
    """Reference to evidence from user profile."""
    type: str  # "experience", "project", "skill", "education"
    id: int
    bullet_idx: Optional[int] = None  # For bullets within experience/project
    text: Optional[str] = None  # The actual evidence text


class EvidenceMapSchema(BaseModel):
    """Mapping of JD requirements to profile evidence."""
    jd_structured: JDStructuredSchema
    matched_items: dict  # {"responsibility": [EvidenceRef], "must_have_skills": [EvidenceRef], ...}
    missing_items: List[dict] = []  # [{"type": "skill", "name": "Kubernetes", "reason": "not_found"}]
    match_score: float = 0.0  # Overall match percentage
