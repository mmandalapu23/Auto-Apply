"""Profile service."""
import json
from sqlalchemy.orm import Session
from app.db.models import Profile, Experience, Project, Education, Skill
from app.schemas.profile import ProfileSchema, ProfileUpdateRequest
from app.schemas.profile import (
    ExperienceSchema, ProjectSchema, EducationSchema, SkillSchema,
    ExperienceBulletSchema, ProjectBulletSchema
)


class ProfileService:
    """Profile management."""
    
    @staticmethod
    def get_or_create_profile(db: Session, user_id: int) -> Profile:
        """Get existing profile or create new one."""
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            # Create default profile
            profile = Profile(user_id=user_id, email="")
            db.add(profile)
            db.commit()
            db.refresh(profile)
        return profile
    
    @staticmethod
    def get_profile(db: Session, user_id: int) -> Profile:
        """Get user profile."""
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            raise ValueError(f"Profile for user {user_id} not found")
        return profile
    
    @staticmethod
    def update_profile(db: Session, user_id: int, request: ProfileUpdateRequest) -> Profile:
        """Update user profile."""
        profile = ProfileService.get_profile(db, user_id)
        
        # Update basic info
        profile.email = request.email
        profile.phone = request.phone
        profile.location = request.location
        profile.summary = request.summary
        profile.degree = request.degree
        profile.university = request.university
        profile.graduation_year = request.graduation_year
        
        # Clear and rebuild experiences
        db.query(Experience).filter(Experience.profile_id == profile.id).delete()
        for exp_data in request.experiences:
            bullets_json = json.dumps([{
                "text": b.text,
                "tech": b.tech
            } for b in exp_data.bullets])
            
            exp = Experience(
                profile_id=profile.id,
                company=exp_data.company,
                title=exp_data.title,
                start_date=exp_data.start_date,
                end_date=exp_data.end_date,
                is_current=exp_data.is_current if hasattr(exp_data, 'is_current') else False,
                description=bullets_json if exp_data.bullets else None
            )
            db.add(exp)
        
        # Clear and rebuild projects
        db.query(Project).filter(Project.profile_id == profile.id).delete()
        for proj_data in request.projects:
            bullets_json = json.dumps([{
                "text": b.text,
                "tech": b.tech
            } for b in proj_data.bullets])
            
            proj = Project(
                profile_id=profile.id,
                name=proj_data.name,
                description=bullets_json if proj_data.bullets else None,
                url=proj_data.url
            )
            db.add(proj)
        
        # Clear and rebuild educations
        db.query(Education).filter(Education.profile_id == profile.id).delete()
        for edu_data in request.educations:
            edu = Education(
                profile_id=profile.id,
                institution=edu_data.institution,
                degree=edu_data.degree,
                field=edu_data.field,
                start_date=edu_data.start_date,
                end_date=edu_data.end_date,
                gpa=edu_data.gpa
            )
            db.add(edu)
        
        # Clear and rebuild skills
        db.query(Skill).filter(Skill.profile_id == profile.id).delete()
        for skill_data in request.skills:
            skill = Skill(
                profile_id=profile.id,
                name=skill_data.name,
                category=skill_data.category,
                proficiency=skill_data.proficiency
            )
            db.add(skill)
        
        db.commit()
        db.refresh(profile)
        return profile
    
    @staticmethod
    def profile_to_schema(profile: Profile) -> ProfileSchema:
        """Convert ORM to schema."""
        experiences = []
        for exp in profile.experiences:
            bullets = []
            if exp.description:
                try:
                    bullets_data = json.loads(exp.description) if isinstance(exp.description, str) else []
                    bullets = [ExperienceBulletSchema(**b) for b in bullets_data]
                except:
                    pass
            
            experiences.append(ExperienceSchema(
                id=exp.id,
                company=exp.company,
                title=exp.title,
                start_date=exp.start_date,
                end_date=exp.end_date,
                is_current=exp.is_current,
                bullets=bullets
            ))
        
        projects = []
        for proj in profile.projects:
            bullets = []
            if proj.description:
                try:
                    bullets_data = json.loads(proj.description) if isinstance(proj.description, str) else []
                    bullets = [ProjectBulletSchema(**b) for b in bullets_data]
                except:
                    pass
            
            projects.append(ProjectSchema(
                id=proj.id,
                name=proj.name,
                bullets=bullets,
                url=proj.url
            ))
        
        educations = [EducationSchema.from_orm(e) for e in profile.educations]
        skills = [SkillSchema.from_orm(s) for s in profile.skills]
        
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
            updated_at=profile.updated_at
        )
