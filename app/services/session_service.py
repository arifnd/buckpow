from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.models import Session
from app.utils.pagination import PaginatedResult


class SessionService:

    @staticmethod
    def get_all(db: Session):
        return db.query(Session).options(selectinload(Session.device_ref), selectinload(Session.project)).order_by(Session.created_at.desc()).all()

    @staticmethod
    def get_paginated(db: Session, page=1, per_page=10):
        q = db.query(Session).options(selectinload(Session.device_ref), selectinload(Session.project)).order_by(Session.created_at.desc())
        offset = (page - 1) * per_page
        total = q.count()
        items = q.offset(offset).limit(per_page).all()
        pages = (total + per_page - 1) // per_page if total > 0 else 1
        return PaginatedResult(items=items, page=page, pages=pages, total=total, per_page=per_page)

    @staticmethod
    def get_by_id(db: Session, session_id):
        return db.get(Session, session_id)

    @staticmethod
    def get_active_session(db: Session, device_id):
        return db.query(Session).filter_by(
            device_id=device_id, status='running'
        ).first()

    @staticmethod
    def create(db: Session, device_id, name, target_device='', description='', project_id=None):
        session = Session(
            device_id=device_id,
            name=name,
            target_device=target_device,
            description=description,
            status='draft',
            project_id=project_id,
        )
        db.add(session)
        db.commit()
        return session

    @staticmethod
    def update(db: Session, session_id, **kwargs):
        session = db.get(Session, session_id)
        if not session:
            return None
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        db.commit()
        return session

    @staticmethod
    def delete(db: Session, session_id):
        session = db.get(Session, session_id)
        if not session:
            return False
        db.delete(session)
        db.commit()
        return True

    @staticmethod
    def start(db: Session, session_id):
        session = db.get(Session, session_id)
        if not session:
            return None, 'Session not found'
        if session.status == 'running':
            return None, 'Session is already running'

        device_running = SessionService.get_active_session(db, session.device_id)
        if device_running and device_running.id != session.id:
            return None, 'A session is already running for this device'

        session.status = 'running'
        session.started_at = datetime.now(timezone.utc)
        session.ended_at = None
        db.commit()
        db.refresh(session)
        return session, None

    @staticmethod
    def stop(db: Session, session_id):
        session = db.get(Session, session_id)
        if not session:
            return None, 'Session not found'
        if session.status != 'running':
            return None, 'Session is not running'
        session.status = 'finished'
        session.ended_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(session)
        return session, None

    @staticmethod
    def get_for_device(db: Session, device_id):
        return db.query(Session).filter_by(device_id=device_id).order_by(Session.created_at.desc()).all()

    @staticmethod
    def get_stats_for_sessions(db: Session, session_ids):
        if not session_ids:
            return {}
        from app.models import Measurement
        rows = db.query(
            Measurement.session_id,
            func.avg(Measurement.power).label('avg_power'),
            func.max(Measurement.energy).label('last_energy'),
            func.min(Measurement.energy).label('first_energy'),
        ).filter(
            Measurement.session_id.in_(session_ids),
            Measurement.session_id.isnot(None),
        ).group_by(Measurement.session_id).all()
        result = {}
        for r in rows:
            total = (r.last_energy or 0) - (r.first_energy or 0)
            result[r.session_id] = {
                'avg_power': round(r.avg_power, 2) if r.avg_power is not None else None,
                'total_energy': round(total, 2) if total > 0 else 0.0,
            }
        return result
