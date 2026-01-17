"""Resume generation and rendering schemas."""
from pydantic import BaseModel
from typing import List, Optional
from app.schemas.jd import EvidenceRefSchema


class ResumeBulletSchema(BaseModel):
    """Individual resume bullet."""
    text: str
    evidence_refs: List[EvidenceRefSchema] = []
    needs_user_input: Optional[str] = None  # Reason if cannot support


class ResumeSummarySchema(BaseModel):
    """Resume summary section."""
    text: str
    evidence_refs: List[EvidenceRefSchema] = []


class ResumeExperienceSchema(BaseModel):
    """Resume experience section."""
    company: str
    title: str
    start_date: str  # MM/YYYY
    end_date: Optional[str] = None
    bullets: List[ResumeBulletSchema] = []
    evidence_refs: List[EvidenceRefSchema] = []


class ResumeProjectSchema(BaseModel):
    """Resume project section."""
    name: str
    bullets: List[ResumeBulletSchema] = []
    evidence_refs: List[EvidenceRefSchema] = []


class ResumeEducationSchema(BaseModel):
    """Resume education section."""
    institution: str
    degree: str
    field: Optional[str] = None
    graduation_date: Optional[str] = None  # MM/YYYY


class ResumeStructuredSchema(BaseModel):
    """Fully structured resume."""
    summary: ResumeSummarySchema
    skills: List[str]
    experience: List[ResumeExperienceSchema]
    projects: List[ResumeProjectSchema]
    education: List[ResumeEducationSchema]


class GenerateResumeRequest(BaseModel):
    """Request to generate resume."""
    job_id: int


class ResumePDFRequest(BaseModel):
    """Request to render resume to PDF."""
    resume_id: int
