from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import AuditLog
from app.utils.pagination import PaginatedResult


class AuditService:

    @staticmethod
    def log(db: Session, action, user_id=None, target_type=None, target_id=None, details=None, ip_address=None):
        entry = AuditLog(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
            ip_address=ip_address,
        )
        db.add(entry)
        db.commit()
        return entry

    @staticmethod
    def get_paginated(db: Session, page=1, per_page=10, action=None, target_type=None):
        q = db.query(AuditLog)
        if action:
            q = q.filter_by(action=action)
        if target_type:
            q = q.filter_by(target_type=target_type)
        q = q.order_by(AuditLog.created_at.desc())
        offset = (page - 1) * per_page
        total = q.count()
        items = q.offset(offset).limit(per_page).all()
        pages = (total + per_page - 1) // per_page if total > 0 else 1
        return PaginatedResult(items=items, page=page, pages=pages, total=total, per_page=per_page)

    @staticmethod
    def get_actions(db: Session):
        rows = db.query(AuditLog.action).distinct().order_by(AuditLog.action).all()
        return [r[0] for r in rows]
