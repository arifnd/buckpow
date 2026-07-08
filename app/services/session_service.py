from datetime import datetime, timezone

from app import db
from app.models import Session


class SessionService:

    @staticmethod
    def get_all():
        return Session.query.order_by(Session.created_at.desc()).all()

    @staticmethod
    def get_by_id(session_id):
        return db.session.get(Session, session_id)

    @staticmethod
    def get_active_session(device_id):
        return Session.query.filter_by(
            device_id=device_id, status='running'
        ).first()

    @staticmethod
    def create(device_id, name, target_device='', description=''):
        session = Session(
            device_id=device_id,
            name=name,
            target_device=target_device,
            description=description,
            status='draft',
        )
        db.session.add(session)
        db.session.commit()
        return session

    @staticmethod
    def update(session_id, **kwargs):
        session = db.session.get(Session, session_id)
        if not session:
            return None
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        db.session.commit()
        return session

    @staticmethod
    def delete(session_id):
        session = db.session.get(Session, session_id)
        if not session:
            return False
        db.session.delete(session)
        db.session.commit()
        return True

    @staticmethod
    def start(session_id):
        session = db.session.get(Session, session_id)
        if not session:
            return None, 'Session not found'
        if session.status == 'running':
            return None, 'Session is already running'

        existing = SessionService.get_active_session(session.device_id)
        if existing and existing.id != session.id:
            existing.status = 'finished'
            existing.ended_at = datetime.now(timezone.utc)

        session.status = 'running'
        session.started_at = datetime.now(timezone.utc)
        session.ended_at = None
        db.session.commit()
        return session, None

    @staticmethod
    def stop(session_id):
        session = db.session.get(Session, session_id)
        if not session:
            return None, 'Session not found'
        if session.status != 'running':
            return None, 'Session is not running'
        session.status = 'finished'
        session.ended_at = datetime.now(timezone.utc)
        db.session.commit()
        return session, None

    @staticmethod
    def get_for_device(device_id):
        return Session.query.filter_by(device_id=device_id).order_by(Session.created_at.desc()).all()
