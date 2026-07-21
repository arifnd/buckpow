from sqlalchemy.orm import Session

from src.projects.models import Project
from src.utils.pagination import PaginatedResult


class ProjectService:

    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(Project).order_by(Project.created_at.desc()).all()

    def get_paginated(self, page=1, per_page=10):
        q = self.db.query(Project).order_by(Project.created_at.desc())
        offset = (page - 1) * per_page
        total = q.count()
        items = q.offset(offset).limit(per_page).all()
        pages = (total + per_page - 1) // per_page if total > 0 else 1
        return PaginatedResult(items=items, page=page, pages=pages, total=total, per_page=per_page)

    def get_by_id(self, project_id):
        return self.db.get(Project, project_id)

    def create(self, name, description='', owner_id=None):
        project = Project(
            name=name,
            description=description,
            owner_id=owner_id,
        )
        self.db.add(project)
        self.db.commit()
        return project

    def update(self, project_id, **kwargs):
        project = self.db.get(Project, project_id)
        if not project:
            return None
        for key, value in kwargs.items():
            if hasattr(project, key):
                setattr(project, key, value)
        self.db.commit()
        return project

    def delete(self, project_id):
        project = self.db.get(Project, project_id)
        if not project:
            return False
        self.db.delete(project)
        self.db.commit()
        return True