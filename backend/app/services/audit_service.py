"""Audit service."""
import json
from sqlalchemy.orm import Session
from app.db.models import AuditLog


class AuditService:
    """Audit logging."""
    
    @staticmethod
    def log_action(
        db: Session,
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: int = None,
        details: dict = None,
        context: dict = None
    ) -> AuditLog:
        """Log an action."""
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=json.dumps(details) if details else None,
            context=json.dumps(context) if context else None
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    
    @staticmethod
    def get_logs(
        db: Session,
        user_id: int,
        action: str = None,
        skip: int = 0,
        limit: int = 50
    ) -> list:
        """Get audit logs."""
        query = db.query(AuditLog).filter(AuditLog.user_id == user_id)
        if action:
            query = query.filter(AuditLog.action == action)
        return query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
