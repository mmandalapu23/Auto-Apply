"""Profile service."""
from __future__ import annotations

import json
from typing import List, Optional, Sequence, Type

from sqlalchemy.orm import Session

from app.db.models import Education, Experience, Profile, Project, Skill
from app.schemas.profile import (
    EducationSchema,
    ExperienceBulletSchema,
    ExperienceSchema,
    ProfileSchema,
    ProfileUpdateRequest,
    ProjectBulletSchema,
    ProjectSchema,
    SkillSchema,
)


class ProfileService:
    """Handles read/write operations for user profiles."""

    @staticmethod
    def get_or_create(db: Session, user_id: int) -> Profile:
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if profile:
            return profile

        profile = Profile(user_id=user_id, email="")
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def get(db: Session, user_id: int) -> Profile:
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            raise ValueError(f"Profile for user {user_id} not found")
        return profile

    @staticmethod
    def update(db: Session, user_id: int, request: ProfileUpdateRequest) -> Profile:
        profile = ProfileService.get(db, user_id)

        profile.email = request.email
        profile.phone = request.phone
        profile.location = request.location
        profile.summary = request.summary
        profile.degree = request.degree
        profile.university = request.university
        profile.graduation_year = request.graduation_year

        ProfileService._replace_experiences(db, profile.id, request.experiences)
        ProfileService._replace_projects(db, profile.id, request.projects)
        ProfileService._replace_education(db, profile.id, request.educations)
        ProfileService._replace_skills(db, profile.id, request.skills)

        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def to_schema(profile: Profile) -> ProfileSchema:
        experiences = [
            ExperienceSchema(
                id=exp.id,
                company=exp.company,
                title=exp.title,
                start_date=exp.start_date,
                end_date=exp.end_date,
                is_current=exp.is_current,
                bullets=ProfileService._load_bullets(exp.description, ExperienceBulletSchema),
            )
            for exp in profile.experiences
        ]

        projects = [
            ProjectSchema(
                id=proj.id,
                name=proj.name,
                bullets=ProfileService._load_bullets(proj.description, ProjectBulletSchema),
                url=proj.url,
            )
            for proj in profile.projects
        ]

        educations = [EducationSchema.from_orm(edu) for edu in profile.educations]
        skills = [SkillSchema.from_orm(skill) for skill in profile.skills]

        return ProfileSchema(
            id=profile.id,
            user_id=profile.user_id,
            email=profile.email,
            phone=profile.phone,
            location=profile.location,
            summary=profile.summary,
            degree=profile.degree,
            university=profile.university,
            graduation_year=profile.graduation_year,
            experiences=experiences,
            projects=projects,
            educations=educations,
            skills=skills,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )

    # Backwards compatible namespaces
    get_or_create_profile = get_or_create
    get_profile = get
    update_profile = update
    profile_to_schema = to_schema

    # Internal helpers -------------------------------------------------
    @staticmethod
    def _replace_experiences(db: Session, profile_id: int, experiences: Sequence) -> None:
        db.query(Experience).filter(Experience.profile_id == profile_id).delete()
        for exp in experiences:
            bullets = ProfileService._dump_bullets(exp.bullets)
            db.add(
                Experience(
                    profile_id=profile_id,
                    company=exp.company,
                    title=exp.title,
                    start_date=exp.start_date,
                    end_date=exp.end_date,
                    is_current=getattr(exp, "is_current", False),
                    description=bullets,
                )
            )

    @staticmethod
    def _replace_projects(db: Session, profile_id: int, projects: Sequence) -> None:
        db.query(Project).filter(Project.profile_id == profile_id).delete()
        for proj in projects:
            bullets = ProfileService._dump_bullets(proj.bullets)
            db.add(
                Project(
                    profile_id=profile_id,
                    name=proj.name,
                    description=bullets,
                    url=proj.url,
                )
            )

    @staticmethod
    def _replace_education(db: Session, profile_id: int, educations: Sequence) -> None:
        db.query(Education).filter(Education.profile_id == profile_id).delete()
        for edu in educations:
            db.add(
                Education(
                    profile_id=profile_id,
                    institution=edu.institution,
                    degree=edu.degree,
                    field=edu.field,
                    start_date=edu.start_date,
                    end_date=edu.end_date,
                    gpa=edu.gpa,
                )
            )

    @staticmethod
    def _replace_skills(db: Session, profile_id: int, skills: Sequence) -> None:
        db.query(Skill).filter(Skill.profile_id == profile_id).delete()
        for skill in skills:
            db.add(
                Skill(
                    profile_id=profile_id,
                    name=skill.name,
                    category=skill.category,
                    proficiency=skill.proficiency,
                )
            )

    @staticmethod
    def _dump_bullets(bullets: Sequence) -> Optional[str]:
        if not bullets:
            return None
        return json.dumps([{"text": b.text, "tech": b.tech} for b in bullets])

    @staticmethod
    def _load_bullets(serialized: str, schema_cls: Type) -> List:
        if not serialized:
            return []
        try:
            data = json.loads(serialized) if isinstance(serialized, str) else []
            return [schema_cls(**item) for item in data]
        except (TypeError, ValueError):
            return []
