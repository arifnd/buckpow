from sqlalchemy.orm import Session

from app.models import Project


class ProjectService:

    @staticmethod
    def get_all(db: Session):
        return db.query(Project).order_by(Project.created_at.desc()).all()

    @staticmethod
    def get_paginated(db: Session, page=1, per_page=10):
        q = db.query(Project).order_by(Project.created_at.desc())
        offset = (page - 1) * per_page
        total = q.count()
        items = q.offset(offset).limit(per_page).all()
        pages = (total + per_page - 1) // per_page if total > 0 else 1
        return type('Pagination', (), {'items': items, 'page': page, 'pages': pages, 'total': total, 'per_page': per_page})()

    @staticmethod
    def get_by_id(db: Session, project_id):
        return db.get(Project, project_id)

    @staticmethod
    def create(db: Session, name, description='', owner_id=None):
        project = Project(
            name=name,
            description=description,
            owner_id=owner_id,
        )
        db.add(project)
        db.commit()
        return project

    @staticmethod
    def update(db: Session, project_id, **kwargs):
        project = db.get(Project, project_id)
        if not project:
            return None
        for key, value in kwargs.items():
            if hasattr(project, key):
                setattr(project, key, value)
        db.commit()
        return project

    @staticmethod
    def delete(db: Session, project_id):
        project = db.get(Project, project_id)
        if not project:
            return False
        db.delete(project)
        db.commit()
        return True
