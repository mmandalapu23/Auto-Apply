"""Profile-related schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SkillSchema(BaseModel):
    """Skill."""
    id: Optional[int] = None
    name: str
    category: Optional[str] = None
    proficiency: Optional[str] = None
    
    class Config:
        from_attributes = True


class ExperienceBulletSchema(BaseModel):
    """Individual bullet point in experience."""
    text: str
    tech: List[str] = Field(default_factory=list)


class ExperienceSchema(BaseModel):
    """Work experience."""
    id: Optional[int] = None
    company: str
    title: str
    start_date: str  # YYYY-MM
    end_date: Optional[str] = None  # YYYY-MM
    is_current: bool = False
    bullets: List[ExperienceBulletSchema] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class ProjectBulletSchema(BaseModel):
    """Individual bullet point in project."""
    text: str
    tech: List[str] = Field(default_factory=list)


class ProjectSchema(BaseModel):
    """Project."""
    id: Optional[int] = None
    name: str
    bullets: List[ProjectBulletSchema] = Field(default_factory=list)
    url: Optional[str] = None
    
    class Config:
        from_attributes = True


class EducationSchema(BaseModel):
    """Education."""
    id: Optional[int] = None
    institution: str
    degree: str
    field: Optional[str] = None
    start_date: Optional[str] = None  # YYYY-MM
    end_date: Optional[str] = None  # YYYY-MM
    gpa: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProfileSchema(BaseModel):
    """User profile."""
    id: Optional[int] = None
    user_id: int
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    degree: Optional[str] = None
    university: Optional[str] = None
    graduation_year: Optional[int] = None
    
    experiences: List[ExperienceSchema] = Field(default_factory=list)
    projects: List[ProjectSchema] = Field(default_factory=list)
    educations: List[EducationSchema] = Field(default_factory=list)
    skills: List[SkillSchema] = Field(default_factory=list)
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProfileUpdateRequest(BaseModel):
    """Update profile request."""
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    degree: Optional[str] = None
    university: Optional[str] = None
    graduation_year: Optional[int] = None
    experiences: List[ExperienceSchema] = Field(default_factory=list)
    projects: List[ProjectSchema] = Field(default_factory=list)
    educations: List[EducationSchema] = Field(default_factory=list)
    skills: List[SkillSchema] = Field(default_factory=list)
