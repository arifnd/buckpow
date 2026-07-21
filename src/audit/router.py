from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import User
from src.dependencies import require_user
from src.audit.service import AuditService

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
    pagination = AuditService(db).get_paginated(page=page, per_page=per_page,
        action=action, target_type=target_type,
    )
    return {
        'logs': [l.to_dict() for l in pagination.items],
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total,
        'per_page': pagination.per_page,
        'actions': AuditService(db).get_actions(),
    }
