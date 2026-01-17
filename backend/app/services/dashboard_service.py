"""Dashboard and analytics service for user metrics."""
from datetime import datetime, timedelta
from typing import Dict, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import Job, Application, ApplicationStatus


class DashboardService:
    """Calculate dashboard metrics and job trends."""

    @staticmethod
    def get_daily_metrics(db: Session, user_id: int) -> Dict:
        """Get today's job and application metrics."""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        # Today's saved jobs
        saved_today = db.query(func.count(Job.id)).filter(
            Job.user_id == user_id,
            Job.created_at >= today_start,
            Job.created_at < today_end,
        ).scalar() or 0
        
        # Today's applications
        applications_today = db.query(func.count(Application.id)).filter(
            Application.user_id == user_id,
            Application.created_at >= today_start,
            Application.created_at < today_end,
        ).scalar() or 0
        
        # Applications submitted today
        submitted_today = db.query(func.count(Application.id)).filter(
            Application.user_id == user_id,
            Application.status == ApplicationStatus.SUBMITTED,
            Application.updated_at >= today_start,
            Application.updated_at < today_end,
        ).scalar() or 0
        
        return {
            "date": today_start.date().isoformat(),
            "jobs_saved": saved_today,
            "applications_prepared": applications_today,
            "applications_submitted": submitted_today,
        }

    @staticmethod
    def get_weekly_metrics(db: Session, user_id: int) -> Dict:
        """Get this week's (last 7 days) metrics."""
        week_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=7)
        
        jobs_saved = db.query(func.count(Job.id)).filter(
            Job.user_id == user_id,
            Job.created_at >= week_start,
        ).scalar() or 0
        
        applications_total = db.query(func.count(Application.id)).filter(
            Application.user_id == user_id,
            Application.created_at >= week_start,
        ).scalar() or 0
        
        applications_submitted = db.query(func.count(Application.id)).filter(
            Application.user_id == user_id,
            Application.status == ApplicationStatus.SUBMITTED,
            Application.updated_at >= week_start,
        ).scalar() or 0
        
        return {
            "period": "last_7_days",
            "jobs_saved": jobs_saved,
            "applications_prepared": applications_total,
            "applications_submitted": applications_submitted,
        }

    @staticmethod
    def get_monthly_metrics(db: Session, user_id: int) -> Dict:
        """Get this month's metrics."""
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        jobs_saved = db.query(func.count(Job.id)).filter(
            Job.user_id == user_id,
            Job.created_at >= month_start,
        ).scalar() or 0
        
        applications_total = db.query(func.count(Application.id)).filter(
            Application.user_id == user_id,
            Application.created_at >= month_start,
        ).scalar() or 0
        
        applications_submitted = db.query(func.count(Application.id)).filter(
            Application.user_id == user_id,
            Application.status == ApplicationStatus.SUBMITTED,
            Application.updated_at >= month_start,
        ).scalar() or 0
        
        return {
            "period": "this_month",
            "jobs_saved": jobs_saved,
            "applications_prepared": applications_total,
            "applications_submitted": applications_submitted,
        }

    @staticmethod
    def get_job_trends(db: Session, user_id: int, days: int = 30) -> List[Dict]:
        """Get job posting trends over last N days."""
        start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days)
        
        # Get daily counts
        daily_counts = db.query(
            func.date(Job.created_at).label("date"),
            func.count(Job.id).label("total"),
            func.sum(Job.is_remote.cast(int)).label("remote"),
        ).filter(
            Job.user_id == user_id,
            Job.created_at >= start_date,
        ).group_by(
            func.date(Job.created_at)
        ).order_by("date").all()
        
        return [
            {
                "date": str(count.date),
                "total_jobs": count.total,
                "remote_jobs": count.remote or 0,
                "onsite_jobs": count.total - (count.remote or 0),
            }
            for count in daily_counts
        ]

    @staticmethod
    def get_role_distribution(db: Session, user_id: int) -> List[Dict]:
        """Get distribution of saved jobs by role category."""
        categories = db.query(
            Job.role_category,
            func.count(Job.id).label("count"),
        ).filter(
            Job.user_id == user_id,
            Job.is_active == True,
            Job.role_category.isnot(None),
        ).group_by(
            Job.role_category
        ).order_by(func.count(Job.id).desc()).all()
        
        return [
            {
                "category": cat[0],
                "count": cat[1],
            }
            for cat in categories
        ]

    @staticmethod
    def get_company_stats(db: Session, user_id: int) -> List[Dict]:
        """Get top companies with most job openings."""
        companies = db.query(
            Job.company,
            func.count(Job.id).label("count"),
        ).filter(
            Job.user_id == user_id,
            Job.is_active == True,
            Job.company.isnot(None),
        ).group_by(
            Job.company
        ).order_by(func.count(Job.id).desc()).limit(10).all()
        
        return [
            {
                "company": comp[0],
                "count": comp[1],
            }
            for comp in companies
        ]

    @staticmethod
    def get_application_funnel(db: Session, user_id: int) -> Dict:
        """Get application status breakdown (funnel)."""
        total_by_status = db.query(
            Application.status,
            func.count(Application.id).label("count"),
        ).filter(
            Application.user_id == user_id,
        ).group_by(
            Application.status
        ).all()
        
        status_map = {
            ApplicationStatus.PENDING: "pending",
            ApplicationStatus.READY_FOR_REVIEW: "ready_for_review",
            ApplicationStatus.SUBMITTED: "submitted",
            ApplicationStatus.COMPLETED: "completed",
        }
        
        total_applications = sum(count for _, count in total_by_status)
        
        return {
            "total_applications": total_applications,
            "by_status": {
                status_map.get(status, str(status)): count
                for status, count in total_by_status
            },
            "completion_rate": (
                next((count for status, count in total_by_status if status == ApplicationStatus.SUBMITTED), 0) / total_applications
                if total_applications > 0
                else 0
            ),
        }
