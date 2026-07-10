from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.auth import require_user
from app.services.audit_service import AuditService

router = APIRouter()


@router.get('/audit/logs')
def list_audit_logs(
    page: int = Query(1),
    per_page: int = Query(10),
    action: str | None = Query(None),
    target_type: str | None = Query(None),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_user),
):
    pagination = AuditService.get_paginated(
        db, page=page, per_page=per_page,
        action=action, target_type=target_type,
    )
    return {
        'logs': [l.to_dict() for l in pagination.items],
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total,
        'per_page': pagination.per_page,
        'actions': AuditService.get_actions(db),
    }
