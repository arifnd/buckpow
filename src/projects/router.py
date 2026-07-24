from fastapi import APIRouter, HTTPException, Request, Query

from src.dependencies import DbDep, RequiredUserDep
from src.projects.service import ProjectService
from src.audit.service import AuditService
from src.utils.client_ip import get_client_ip
from src.projects.schemas import ProjectCreate, ProjectUpdate

router = APIRouter()


@router.get("/projects")
def list_projects(
    db: DbDep,
    current_user: RequiredUserDep,
    page: int = Query(1),
    per_page: int = Query(10),
):
    if page == 0:
        projects = ProjectService(db).get_all()
        return [p.to_dict() for p in projects]
    pagination = ProjectService(db).get_paginated(page=page, per_page=per_page)
    return {
        "projects": [p.to_dict() for p in pagination.items],
        "page": pagination.page,
        "pages": pagination.pages,
        "total": pagination.total,
        "per_page": pagination.per_page,
    }


@router.post("/projects", status_code=201)
def create_project(
    body: ProjectCreate,
    request: Request,
    db: DbDep,
    current_user: RequiredUserDep,
):
    project = ProjectService(db).create(
        name=body.name,
        description=body.description,
        owner_id=current_user.id,
    )
    ip = get_client_ip(request)
    AuditService(db).log(
        "project.create",
        user_id=current_user.id,
        target_type="project",
        target_id=project.id,
        ip_address=ip,
    )
    return project.to_dict()


@router.get("/projects/{project_id}")
def get_project(
    project_id: int,
    db: DbDep,
    current_user: RequiredUserDep,
):
    project = ProjectService(db).get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project.to_dict()


@router.put("/projects/{project_id}")
def update_project(
    project_id: int,
    body: ProjectUpdate,
    request: Request,
    db: DbDep,
    current_user: RequiredUserDep,
):
    project = ProjectService(db).get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this project"
        )
    project = ProjectService(db).update(
        project_id,
        name=body.name,
        description=body.description,
    )
    ip = get_client_ip(request)
    AuditService(db).log(
        "project.update",
        user_id=current_user.id,
        target_type="project",
        target_id=project_id,
        ip_address=ip,
    )
    return project.to_dict()


@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    request: Request,
    db: DbDep,
    current_user: RequiredUserDep,
):
    project = ProjectService(db).get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this project"
        )
    if ProjectService(db).delete(project_id):
        ip = get_client_ip(request)
        AuditService(db).log(
            "project.delete",
            user_id=current_user.id,
            target_type="project",
            target_id=project_id,
            ip_address=ip,
        )
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Project not found")
