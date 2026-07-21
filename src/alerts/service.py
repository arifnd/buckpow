from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from src.alerts.models import Alert
from src.config import settings
from src.utils.pagination import PaginatedResult
from src.utils.query import FilterBuilder

DEFAULT_HIGH_POWER_THRESHOLD = 2.5
DEFAULT_HIGH_CURRENT_THRESHOLD = 0.5
DEFAULT_LOW_VOLTAGE_THRESHOLD = 4.5


class AlertService:

    def __init__(self, db: Session):
        self.db = db

    def create(self, device_id, level, message):
        alert = Alert(device_id=device_id, level=level, message=message)
        self.db.add(alert)
        self.db.commit()
        return alert

    def get_paginated(self, page=1, per_page=10, device_id=None, level=None, resolved=None):
        fb = FilterBuilder(Alert, self.db.query(Alert))
        fb.eq(device_id=device_id, level=level).order('created_at')
        if resolved is True:
            fb.query = fb.query.filter(Alert.resolved_at.isnot(None))
        elif resolved is False:
            fb.query = fb.query.filter(Alert.resolved_at.is_(None))
        return fb.paginate(page, per_page)

    def resolve(self, alert_id):
        alert = self.db.get(Alert, alert_id)
        if not alert:
            return None
        alert.resolved_at = datetime.now(timezone.utc)
        self.db.commit()
        return alert

    def resolve_all(self, device_id=None):
        fb = FilterBuilder(Alert, self.db.query(Alert).filter(Alert.resolved_at.is_(None)))
        fb.eq(device_id=device_id)
        now = datetime.now(timezone.utc)
        for alert in fb.query.all():
            alert.resolved_at = now
        self.db.commit()

    def get_unresolved_count(self, device_id=None):
        fb = FilterBuilder(Alert, self.db.query(Alert).filter(Alert.resolved_at.is_(None)))
        fb.eq(device_id=device_id)
        return fb.query.count()

    def _has_unresolved(self, device_id, message_prefix):
        return self.db.query(Alert).filter(
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

    def generate_alerts(self, device, bus_voltage, current, power):
        now = datetime.now(timezone.utc)

        if device.last_seen:
            last = device.last_seen
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            if now - last > timedelta(seconds=settings.DEVICE_ONLINE_TIMEOUT):
                if not self._has_unresolved(device.id, 'Device offline'):
                    self.create(device.id, 'warning', f'Device offline ({device.device_id}) — no data received for >{settings.DEVICE_ONLINE_TIMEOUT}s')
                if not self._has_unresolved(device.id, 'Device back online'):
                    self.create(device.id, 'info', f'Device back online ({device.device_id})')

        owner_s = self._owner_settings(self.db, device)

        threshold_w = device.high_power_threshold
        if threshold_w is None:
            threshold_w = owner_s.get('high_power_threshold') or DEFAULT_HIGH_POWER_THRESHOLD
        if power > threshold_w:
            if not self._has_unresolved(device.id, 'High power'):
                self.create(device.id, 'critical', f'High power on {device.device_id}: {power:.3f}W (threshold: {threshold_w}W)')

        threshold_a = device.high_current_threshold
        if threshold_a is None:
            threshold_a = owner_s.get('high_current_threshold') or DEFAULT_HIGH_CURRENT_THRESHOLD
        if current > threshold_a:
            if not self._has_unresolved(device.id, 'High current'):
                self.create(device.id, 'critical', f'High current on {device.device_id}: {current:.3f}A (threshold: {threshold_a}A)')

        threshold_v = device.low_voltage_threshold
        if threshold_v is None:
            threshold_v = owner_s.get('low_voltage_threshold') or DEFAULT_LOW_VOLTAGE_THRESHOLD
        if bus_voltage < threshold_v:
            if not self._has_unresolved(device.id, 'Low voltage'):
                self.create(device.id, 'warning', f'Low voltage on {device.device_id}: {bus_voltage:.3f}V (threshold: {threshold_v}V)')