from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import require_user
from app.models import User
from app.services.project_service import ProjectService

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str
    description: str = ''


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


@router.get('/projects')
def list_projects(
    page: int = Query(1),
    per_page: int = Query(10),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    if page == 0:
        projects = ProjectService.get_all(db)
        return [p.to_dict() for p in projects]
    pagination = ProjectService.get_paginated(db, page=page, per_page=per_page)
    return {
        'projects': [p.to_dict() for p in pagination.items],
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total,
        'per_page': pagination.per_page,
    }


@router.post('/projects', status_code=201)
def create_project(
    body: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    project = ProjectService.create(
        db,
        name=body.name,
        description=body.description,
        owner_id=current_user.id,
    )
    return project.to_dict()


@router.get('/projects/{project_id}')
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    project = ProjectService.get_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail='Project not found')
    return project.to_dict()


@router.put('/projects/{project_id}')
def update_project(
    project_id: int,
    body: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    project = ProjectService.update(
        db, project_id,
        name=body.name,
        description=body.description,
    )
    if not project:
        raise HTTPException(status_code=404, detail='Project not found')
    return project.to_dict()


@router.delete('/projects/{project_id}')
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    if ProjectService.delete(db, project_id):
        return {'status': 'deleted'}
    raise HTTPException(status_code=404, detail='Project not found')
