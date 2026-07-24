from fastapi import APIRouter, Query

from src.dependencies import DbDep, RequiredUserDep
from src.audit.service import AuditService

router = APIRouter()


@router.get("/audit/logs")
def list_audit_logs(
    db: DbDep,
    _current_user: RequiredUserDep,
    page: int = Query(1),
    per_page: int = Query(10),
    action: str | None = Query(None),
    target_type: str | None = Query(None),
):
    pagination = AuditService(db).get_paginated(
        page=page,
        per_page=per_page,
        action=action,
        target_type=target_type,
    )
    return {
        "logs": [log.to_dict() for log in pagination.items],
        "page": pagination.page,
        "pages": pagination.pages,
        "total": pagination.total,
        "per_page": pagination.per_page,
        "actions": AuditService(db).get_actions(),
    }
