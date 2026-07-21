from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import AuditLog
from app.utils.pagination import PaginatedResult


class AuditService:

    def __init__(self, db: Session):
        self.db = db

    def log(self, action, user_id=None, target_type=None, target_id=None, details=None, ip_address=None):
        entry = AuditLog(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
            ip_address=ip_address,
        )
        self.db.add(entry)
        self.db.commit()
        return entry

    def get_paginated(self, page=1, per_page=10, action=None, target_type=None):
        q = self.db.query(AuditLog)
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

    def get_actions(self):
        rows = self.db.query(AuditLog.action).distinct().order_by(AuditLog.action).all()
        return [r[0] for r in rows]