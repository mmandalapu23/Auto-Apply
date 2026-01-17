"""Request/response schemas."""
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.profile import (
    SkillSchema, ExperienceBulletSchema, ExperienceSchema, 
    ProjectBulletSchema, ProjectSchema, EducationSchema, ProfileSchema, ProfileUpdateRequest
)
from app.schemas.job import JobCreateRequest, JobSchema, JobDetailSchema, JobImportRequest
from app.schemas.jd import (
    JDExtractRequest, ResponsibilitySchema, JDStructuredSchema, 
    EvidenceRefSchema, EvidenceMapSchema
)
from app.schemas.resume import (
    ResumeBulletSchema, ResumeSummarySchema, ResumeExperienceSchema,
    ResumeProjectSchema, ResumeEducationSchema, ResumeStructuredSchema,
    GenerateResumeRequest, ResumePDFRequest
)
from app.schemas.application import (
    ApplicationSchema, ApplicationCreateRequest, 
    ApplicationStatusUpdateRequest, ScheduleSettingsRequest
)
from app.schemas.matching import MatchingScoreSchema, MissingRequirementSchema

__all__ = [
    # Auth
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    # Profile
    "SkillSchema",
    "ExperienceBulletSchema",
    "ExperienceSchema",
    "ProjectBulletSchema",
    "ProjectSchema",
    "EducationSchema",
    "ProfileSchema",
    "ProfileUpdateRequest",
    # Job
    "JobCreateRequest",
    "JobSchema",
    "JobDetailSchema",
    "JobImportRequest",
    # JD
    "JDExtractRequest",
    "ResponsibilitySchema",
    "JDStructuredSchema",
    "EvidenceRefSchema",
    "EvidenceMapSchema",
    # Resume
    "ResumeBulletSchema",
    "ResumeSummarySchema",
    "ResumeExperienceSchema",
    "ResumeProjectSchema",
    "ResumeEducationSchema",
    "ResumeStructuredSchema",
    "GenerateResumeRequest",
    "ResumePDFRequest",
    # Application
    "ApplicationSchema",
    "ApplicationCreateRequest",
    "ApplicationStatusUpdateRequest",
    "ScheduleSettingsRequest",
    # Matching
    "MatchingScoreSchema",
    "MissingRequirementSchema",
]
