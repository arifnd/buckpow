from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session as OrmSession
from sqlalchemy.orm import selectinload

from src.sessions.models import Session
from src.utils.pagination import PaginatedResult


class SessionService:
    def __init__(self, db: OrmSession):
        self.db = db

    def get_all(self):
        return (
            self.db.query(Session)
            .options(selectinload(Session.device_ref), selectinload(Session.project))
            .order_by(Session.created_at.desc())
            .all()
        )

    def get_paginated(self, page=1, per_page=10):
        q = (
            self.db.query(Session)
            .options(selectinload(Session.device_ref), selectinload(Session.project))
            .order_by(Session.created_at.desc())
        )
        offset = (page - 1) * per_page
        total = q.count()
        items = q.offset(offset).limit(per_page).all()
        pages = (total + per_page - 1) // per_page if total > 0 else 1
        return PaginatedResult(
            items=items, page=page, pages=pages, total=total, per_page=per_page
        )

    def get_by_id(self, session_id):
        return (
            self.db.query(Session)
            .options(
                selectinload(Session.device_ref),
                selectinload(Session.project),
            )
            .filter(Session.id == session_id)
            .first()
        )

    def get_active_session(self, device_id):
        return (
            self.db.query(Session)
            .filter_by(device_id=device_id, status="running")
            .first()
        )

    def create(
        self, device_id, name, target_device="", description="", project_id=None
    ):
        session = Session(
            device_id=device_id,
            name=name,
            target_device=target_device,
            description=description,
            status="draft",
            project_id=project_id,
        )
        self.db.add(session)
        self.db.commit()
        return session

    def update(self, session_id, **kwargs):
        session = self.db.get(Session, session_id)
        if not session:
            return None
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        self.db.commit()
        return session

    def delete(self, session_id):
        session = self.db.get(Session, session_id)
        if not session:
            return False
        self.db.delete(session)
        self.db.commit()
        return True

    def start(self, session_id):
        session = self.db.get(Session, session_id)
        if not session:
            return None, "Session not found"
        if session.status == "running":
            return None, "Session is already running"

        device_running = self.get_active_session(session.device_id)
        if device_running and device_running.id != session.id:
            return None, "A session is already running for this device"

        session.status = "running"
        session.started_at = datetime.now(timezone.utc)
        session.ended_at = None
        self.db.commit()
        self.db.refresh(session)
        return session, None

    def stop(self, session_id):
        session = self.db.get(Session, session_id)
        if not session:
            return None, "Session not found"
        if session.status != "running":
            return None, "Session is not running"
        session.status = "finished"
        session.ended_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(session)
        return session, None

    def get_for_device(self, device_id):
        return (
            self.db.query(Session)
            .filter_by(device_id=device_id)
            .order_by(Session.created_at.desc())
            .all()
        )

    @staticmethod
    def get_stats_for_sessions(db: Session, session_ids):
        if not session_ids:
            return {}
        from src.measurements.models import Measurement

        rows = (
            db.query(
                Measurement.session_id,
                func.avg(Measurement.power).label("avg_power"),
            )
            .filter(
                Measurement.session_id.in_(session_ids),
                Measurement.session_id.isnot(None),
            )
            .group_by(Measurement.session_id)
            .all()
        )

        subq = (
            db.query(
                Measurement.session_id,
                func.max(Measurement.id).label("max_id"),
            )
            .filter(
                Measurement.session_id.in_(session_ids),
                Measurement.session_id.isnot(None),
            )
            .group_by(Measurement.session_id)
            .subquery()
        )

        last_rows = (
            db.query(
                subq.c.session_id,
                Measurement.energy.label("last_energy"),
            )
            .join(Measurement, Measurement.id == subq.c.max_id)
            .all()
        )

        last_energy_map = {r.session_id: r.last_energy for r in last_rows}

        result = {}
        for r in rows:
            energy = last_energy_map.get(r.session_id) or 0
            result[r.session_id] = {
                "avg_power": round(r.avg_power, 2) if r.avg_power is not None else None,
                "total_energy": round(energy, 2) if energy > 0 else 0.0,
            }
        return result
