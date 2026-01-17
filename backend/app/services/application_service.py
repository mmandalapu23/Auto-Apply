"""Application service."""
import json
from sqlalchemy.orm import Session
from app.db.models import Application, ApplicationStatus
from app.schemas.application import ApplicationSchema, ApplicationCreateRequest


class ApplicationService:
    """Application management."""
    
    @staticmethod
    def create_application(
        db: Session,
        user_id: int,
        job_id: int,
        resume_id: int = None,
        match_score: dict = None,
        missing_requirements: list = None
    ) -> Application:
        """Create application record."""
        app = Application(
            user_id=user_id,
            job_id=job_id,
            resume_id=resume_id,
            status=ApplicationStatus.READY_FOR_REVIEW,
            match_score=json.dumps(match_score) if match_score else None,
            missing_requirements=json.dumps(missing_requirements) if missing_requirements else None
        )
        db.add(app)
        db.commit()
        db.refresh(app)
        return app
    
    @staticmethod
    def get_application(db: Session, app_id: int, user_id: int) -> Application:
        """Get application (user-scoped)."""
        app = db.query(Application).filter(
            Application.id == app_id,
            Application.user_id == user_id
        ).first()
        if not app:
            raise ValueError(f"Application {app_id} not found")
        return app
    
    @staticmethod
    def list_applications(
        db: Session,
        user_id: int,
        status: str = None,
        skip: int = 0,
        limit: int = 50
    ) -> list:
        """List user's applications."""
        query = db.query(Application).filter(Application.user_id == user_id)
        if status:
            query = query.filter(Application.status == status)
        return query.order_by(Application.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_status(db: Session, app_id: int, status: str) -> Application:
        """Update application status."""
        app = db.query(Application).filter(Application.id == app_id).first()
        if not app:
            raise ValueError(f"Application {app_id} not found")
        
        app.status = status
        db.commit()
        db.refresh(app)
        return app
