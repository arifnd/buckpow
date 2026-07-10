from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from app.models import Alert
from app.config import settings

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
        q = db.query(Alert)
        if device_id:
            q = q.filter_by(device_id=device_id)
        if level:
            q = q.filter_by(level=level)
        if resolved is True:
            q = q.filter(Alert.resolved_at.isnot(None))
        elif resolved is False:
            q = q.filter(Alert.resolved_at.is_(None))
        q = q.order_by(Alert.created_at.desc())
        offset = (page - 1) * per_page
        total = q.count()
        items = q.offset(offset).limit(per_page).all()
        pages = (total + per_page - 1) // per_page if total > 0 else 1
        return type('Pagination', (), {'items': items, 'page': page, 'pages': pages, 'total': total, 'per_page': per_page})()

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
        q = db.query(Alert).filter(Alert.resolved_at.is_(None))
        if device_id:
            q = q.filter_by(device_id=device_id)
        now = datetime.now(timezone.utc)
        for alert in q.all():
            alert.resolved_at = now
        db.commit()

    @staticmethod
    def get_unresolved_count(db: Session, device_id=None):
        q = db.query(Alert).filter(Alert.resolved_at.is_(None))
        if device_id:
            q = q.filter_by(device_id=device_id)
        return q.count()

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
