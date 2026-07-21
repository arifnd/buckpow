from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from app.models import Alert
from app.config import settings
from app.utils.pagination import PaginatedResult
from app.utils.query import FilterBuilder

DEFAULT_HIGH_POWER_THRESHOLD = 2.5
DEFAULT_HIGH_CURRENT_THRESHOLD = 0.5
DEFAULT_LOW_VOLTAGE_THRESHOLD = 4.5


class AlertService:

    @staticmethod
    def create(db: Session, device_id, level, message):
        alert = Alert(device_id=device_id, level=level, message=message)
        db.add(alert)
        db.commit()
        return alert

    @staticmethod
    def get_paginated(db: Session, page=1, per_page=10, device_id=None, level=None, resolved=None):
        fb = FilterBuilder(Alert, db.query(Alert))
        fb.eq(device_id=device_id, level=level).order('created_at')
        if resolved is True:
            fb.query = fb.query.filter(Alert.resolved_at.isnot(None))
        elif resolved is False:
            fb.query = fb.query.filter(Alert.resolved_at.is_(None))
        return fb.paginate(page, per_page)

    @staticmethod
    def resolve(db: Session, alert_id):
        alert = db.get(Alert, alert_id)
        if not alert:
            return None
        alert.resolved_at = datetime.now(timezone.utc)
        db.commit()
        return alert

    @staticmethod
    def resolve_all(db: Session, device_id=None):
        fb = FilterBuilder(Alert, db.query(Alert).filter(Alert.resolved_at.is_(None)))
        fb.eq(device_id=device_id)
        now = datetime.now(timezone.utc)
        for alert in fb.query.all():
            alert.resolved_at = now
        db.commit()

    @staticmethod
    def get_unresolved_count(db: Session, device_id=None):
        fb = FilterBuilder(Alert, db.query(Alert).filter(Alert.resolved_at.is_(None)))
        fb.eq(device_id=device_id)
        return fb.query.count()

    @staticmethod
    def _has_unresolved(db: Session, device_id, message_prefix):
        return db.query(Alert).filter(
            Alert.device_id == device_id,
            Alert.resolved_at.is_(None),
            Alert.message.startswith(message_prefix),
        ).count() > 0

    @staticmethod
    def _owner_settings(db: Session, device):
        try:
            owner = device.project.owner
            return owner.settings or {} if owner else {}
        except Exception:
            return {}

    @staticmethod
    def generate_alerts(db: Session, device, bus_voltage, current, power):
        now = datetime.now(timezone.utc)

        if device.last_seen:
            last = device.last_seen
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            if now - last > timedelta(seconds=settings.DEVICE_ONLINE_TIMEOUT):
                if not AlertService._has_unresolved(db, device.id, 'Device offline'):
                    AlertService.create(db, device.id, 'warning', f'Device offline ({device.device_id}) — no data received for >{settings.DEVICE_ONLINE_TIMEOUT}s')
                if not AlertService._has_unresolved(db, device.id, 'Device back online'):
                    AlertService.create(db, device.id, 'info', f'Device back online ({device.device_id})')

        owner_s = AlertService._owner_settings(db, device)

        threshold_w = device.high_power_threshold
        if threshold_w is None:
            threshold_w = owner_s.get('high_power_threshold') or DEFAULT_HIGH_POWER_THRESHOLD
        if power > threshold_w:
            if not AlertService._has_unresolved(db, device.id, 'High power'):
                AlertService.create(db, device.id, 'critical', f'High power on {device.device_id}: {power:.3f}W (threshold: {threshold_w}W)')

        threshold_a = device.high_current_threshold
        if threshold_a is None:
            threshold_a = owner_s.get('high_current_threshold') or DEFAULT_HIGH_CURRENT_THRESHOLD
        if current > threshold_a:
            if not AlertService._has_unresolved(db, device.id, 'High current'):
                AlertService.create(db, device.id, 'critical', f'High current on {device.device_id}: {current:.3f}A (threshold: {threshold_a}A)')

        threshold_v = device.low_voltage_threshold
        if threshold_v is None:
            threshold_v = owner_s.get('low_voltage_threshold') or DEFAULT_LOW_VOLTAGE_THRESHOLD
        if bus_voltage < threshold_v:
            if not AlertService._has_unresolved(db, device.id, 'Low voltage'):
                AlertService.create(db, device.id, 'warning', f'Low voltage on {device.device_id}: {bus_voltage:.3f}V (threshold: {threshold_v}V)')
