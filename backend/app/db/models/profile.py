"""Profile-related models: experience, education, skills, projects."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base


class Profile(Base):
    """User profile with personal info."""
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Personal info
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    
    # Education
    degree = Column(String, nullable=True)  # e.g., "Bachelor's in Computer Science"
    university = Column(String, nullable=True)
    graduation_year = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    experiences = relationship("Experience", back_populates="profile", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="profile", cascade="all, delete-orphan")
    educations = relationship("Education", back_populates="profile", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="profile", cascade="all, delete-orphan")


class Experience(Base):
    """Work experience entry."""
    __tablename__ = "experiences"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    
    company = Column(String, nullable=False)
    title = Column(String, nullable=False)
    start_date = Column(String, nullable=False)  # YYYY-MM
    end_date = Column(String, nullable=True)  # YYYY-MM or null if current
    is_current = Column(Boolean, default=False)
    
    # Bullet points / achievements
    description = Column(Text, nullable=True)  # JSON string: [{"text": "...", "tech": [...]}, ...]
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    profile = relationship("Profile", back_populates="experiences")


class Project(Base):
    """Personal or professional project."""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)  # JSON: [{"text": "...", "tech": [...]}, ...]
    url = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    profile = relationship("Profile", back_populates="projects")


class Education(Base):
    """Education entry."""
    __tablename__ = "educations"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    
    institution = Column(String, nullable=False)
    degree = Column(String, nullable=False)
    field = Column(String, nullable=True)
    start_date = Column(String, nullable=True)  # YYYY-MM
    end_date = Column(String, nullable=True)  # YYYY-MM
    gpa = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    profile = relationship("Profile", back_populates="educations")


class Skill(Base):
    """Skill entry (can be standalone or tied to experience)."""
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)  # e.g., "Language", "Framework", "Tool"
    proficiency = Column(String, nullable=True)  # e.g., "Expert", "Intermediate", "Beginner"
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    profile = relationship("Profile", back_populates="skills")
