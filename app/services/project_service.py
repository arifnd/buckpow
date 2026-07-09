from app import db
from app.models import Project


class ProjectService:

    @staticmethod
    def get_all():
        return Project.query.order_by(Project.created_at.desc()).all()

    @staticmethod
    def get_paginated(page=1, per_page=10):
        q = Project.query.order_by(Project.created_at.desc())
        return q.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_by_id(project_id):
        return db.session.get(Project, project_id)

    @staticmethod
    def create(name, description='', owner_id=None):
        project = Project(
            name=name,
            description=description,
            owner_id=owner_id,
        )
        db.session.add(project)
        db.session.commit()
        return project

    @staticmethod
    def update(project_id, **kwargs):
        project = db.session.get(Project, project_id)
        if not project:
            return None
        for key, value in kwargs.items():
            if hasattr(project, key):
                setattr(project, key, value)
        db.session.commit()
        return project

    @staticmethod
    def delete(project_id):
        project = db.session.get(Project, project_id)
        if not project:
            return False
        db.session.delete(project)
        db.session.commit()
        return True
