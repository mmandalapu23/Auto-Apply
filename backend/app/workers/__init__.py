"""Workers module."""
from app.workers.celery_app import celery_app
from app.workers.tasks import generate_resume_task, queue_application_task

__all__ = [
    "celery_app",
    "generate_resume_task",
    "queue_application_task",
]
