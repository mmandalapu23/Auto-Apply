"""Background task workers via Celery.

NOTE: This module is for scaling and async task processing (v2.0+):
  - Async resume generation
  - Scheduled application submissions
  - Bulk job imports

For MVP, the API handles requests synchronously.
Enable when Redis and Celery infrastructure is deployed (see docker-compose.yml).
"""
from app.workers.celery_app import celery_app
from app.workers.tasks import generate_resume_task, queue_application_task

__all__ = [
    "celery_app",
    "generate_resume_task",
    "queue_application_task",
]
