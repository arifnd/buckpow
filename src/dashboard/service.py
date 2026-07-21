from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.devices.models import Device
from src.sessions.models import Session
from src.projects.models import Project
from src.measurements.models import Measurement
from src.utils.dates import utc_iso
from src.utils.query import FilterBuilder


class DashboardService:

    def __init__(self, db: Session):
        self.db = db

    def get_summary(self):
        devices = self.db.query(Device).all()
        online = sum(1 for d in devices if d._compute_status() == 'online')
        offline = len(devices) - online
        total_projects = self.db.query(Project).count()
        active_sessions = self.db.query(Session).filter_by(status='running').count()

        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_ms = self.db.query(Measurement).filter(
            Measurement.created_at >= today_start
        ).order_by(Measurement.created_at.asc()).all()

        today_energy = 0.0
        if today_ms:
            seen_sessions = {}
            for m in today_ms:
                if m.session_id:
                    seen_sessions[m.session_id] = m.energy
            today_energy = sum(seen_sessions.values()) if seen_sessions else 0.0

        latest = self.db.query(Measurement).order_by(Measurement.created_at.desc()).first()
        current_power = round(latest.power, 3) if latest else 0.0

        return {
            'online_devices': online,
            'offline_devices': offline,
            'total_projects': total_projects,
            'active_sessions': active_sessions,
            'today_energy': round(today_energy, 6),
            'current_power': current_power,
        }

    def get_statistics(self, device_id=None, session_id=None, start_date=None, end_date=None):
        fb = FilterBuilder(Measurement, self.db.query(Measurement))
        fb.eq(device_id=device_id, session_id=session_id).date_range('created_at', start_date, end_date).order('created_at').limit(500)

        session_started_at = None
        if session_id:
            sess = self.db.query(Session).filter_by(id=session_id, status='running').first()
            if sess:
                session_started_at = utc_iso(sess.started_at)

        rows = fb.query.all()
        if not rows:
            return {
                'voltage': {'min': 0, 'max': 0, 'avg': 0},
                'current': {'min': 0, 'max': 0, 'avg': 0},
                'power': {'min': 0, 'max': 0, 'avg': 0, 'peak': 0},
                'energy': {'hourly': [], 'daily': [], 'weekly': [], 'monthly': []},
                'total_energy': 0,
                'session_started_at': session_started_at,
            }

        from src.measurements.service import MeasurementService

        stats = {
            **MeasurementService._compute_field_stats(rows),
            'energy': self._get_energy_breakdown(
                device_id=device_id, session_id=session_id,
                start_date=start_date, end_date=end_date
            ),
            'total_energy': round(rows[0].energy, 6) if rows else 0,
            'session_started_at': session_started_at,
        }
        return stats

    def _get_energy_breakdown(self, device_id=None, session_id=None,
                              start_date=None, end_date=None):
        fb = FilterBuilder(Measurement, self.db.query(Measurement))
        fb.eq(device_id=device_id, session_id=session_id).date_range('created_at', start_date, end_date).order('created_at', desc=False)
        rows = fb.query.all()
        if not rows:
            return {'hourly': [], 'daily': [], 'weekly': [], 'monthly': []}

        hourly = {}
        daily = {}
        weekly = {}
        monthly = {}
        prev = None
        for m in rows:
            if prev is not None and m.session_id and m.session_id == prev.session_id:
                inc = m.energy - prev.energy
            elif prev is not None:
                inc = 0
            else:
                inc = 0

            if m.created_at:
                hk = m.created_at.strftime('%Y-%m-%dT%H:00:00Z')
                hourly[hk] = hourly.get(hk, 0) + inc

                dk = m.created_at.strftime('%Y-%m-%d')
                daily[dk] = daily.get(dk, 0) + inc

                wk = m.created_at.strftime('%Y-W%W')
                weekly[wk] = weekly.get(wk, 0) + inc

                mk = m.created_at.strftime('%Y-%m')
                monthly[mk] = monthly.get(mk, 0) + inc

            prev = m

        def to_sorted(adict):
            return [{'period': k, 'energy': round(v, 6)} for k, v in sorted(adict.items())]

        return {
            'hourly': to_sorted(hourly),
            'daily': to_sorted(daily),
            'weekly': to_sorted(weekly),
            'monthly': to_sorted(monthly),
        }