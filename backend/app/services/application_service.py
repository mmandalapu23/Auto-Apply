"""Service layer for job applications."""
from __future__ import annotations

import json
from typing import Iterable, Mapping, Optional

from sqlalchemy.orm import Session

from app.db.models import Application, ApplicationStatus
from app.schemas.application import ApplicationCreateRequest, ApplicationSchema


class ApplicationService:
    """Business logic around job applications."""

    @staticmethod
    def create(
        db: Session,
        user_id: int,
        job_id: int,
        resume_id: Optional[int] = None,
        match_score: Optional[Mapping[str, float]] = None,
        missing_requirements: Optional[Iterable[str]] = None,
    ) -> Application:
        """Persist a new application row."""

        application = Application(
            user_id=user_id,
            job_id=job_id,
            resume_id=resume_id,
            status=ApplicationStatus.READY_FOR_REVIEW,
            match_score=json.dumps(match_score) if match_score else None,
            missing_requirements=json.dumps(list(missing_requirements))
            if missing_requirements
            else None,
        )
        db.add(application)
        db.commit()
        db.refresh(application)
        return application

    @staticmethod
    def get(db: Session, application_id: int, user_id: int) -> Application:
        """Fetch an application ensuring it belongs to the user."""

        application = (
            db.query(Application)
            .filter(Application.id == application_id, Application.user_id == user_id)
            .first()
        )
        if not application:
            raise ValueError(f"Application {application_id} not found")
        return application

    @staticmethod
    def list(
        db: Session,
        user_id: int,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Application]:
        """Return applications for a user ordered by recency."""

        query = db.query(Application).filter(Application.user_id == user_id)
        if status:
            query = query.filter(Application.status == status)
        return (
            query.order_by(Application.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_status(db: Session, application_id: int, status: str) -> Application:
        """Update the workflow status for an application."""

        application = db.query(Application).filter(Application.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")

        application.status = status
        db.commit()
        db.refresh(application)
        return application

    @staticmethod
    def to_schema(application: Application) -> ApplicationSchema:
        """Serialize the ORM object into an API schema."""

        match_score = None
        if application.match_score:
            match_score = json.loads(application.match_score)

        missing_requirements = None
        if application.missing_requirements:
            missing_requirements = json.loads(application.missing_requirements)

        return ApplicationSchema(
            id=application.id,
            user_id=application.user_id,
            job_id=application.job_id,
            resume_id=application.resume_id,
            status=application.status,
            match_score=match_score,
            missing_requirements=missing_requirements,
            created_at=application.created_at,
            updated_at=application.updated_at,
        )

    # Backwards compatibility aliases
    create_application = create
    get_application = get
    list_applications = list
