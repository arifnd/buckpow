from datetime import datetime, timezone, timedelta

from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils.dates import utc_iso


ONLINE_TIMEOUT = 30


class Device(Base):
    __tablename__ = 'devices'

    id = Column(Integer, primary_key=True)
    device_id = Column(String(64), unique=True, nullable=False, index=True)
    alias = Column(String(128), default='')
    description = Column(Text, default='')
    sampling_interval = Column(Integer, default=1)
    last_seen = Column(DateTime, nullable=True)
    status = Column(String(16), default='offline')
    enabled = Column(Boolean, default=True)
    firmware_version = Column(String(64), default='')
    api_key = Column(String(64), unique=True, nullable=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    high_current_threshold = Column(Float, nullable=True)
    high_power_threshold = Column(Float, nullable=True)
    low_voltage_threshold = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    sessions = relationship('Session', back_populates='device_ref', lazy='dynamic')
    measurements = relationship('Measurement', back_populates='device_ref', lazy='dynamic')

    def _compute_status(self):
        if not self.last_seen:
            return 'offline'
        last = self.last_seen
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - last < timedelta(seconds=ONLINE_TIMEOUT):
            return 'online'
        return 'offline'

    def _masked_api_key(self):
        if not self.api_key:
            return None
        if len(self.api_key) <= 8:
            return self.api_key[:4] + '****'
        return self.api_key[:6] + '****' + self.api_key[-4:]

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'alias': self.alias,
            'description': self.description,
            'sampling_interval': self.sampling_interval,
            'last_seen': utc_iso(self.last_seen) if self.last_seen else None,
            'status': self._compute_status(),
            'api_key': self._masked_api_key(),
            'enabled': self.enabled,
            'firmware_version': self.firmware_version or '',
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'high_current_threshold': self.high_current_threshold,
            'high_power_threshold': self.high_power_threshold,
            'low_voltage_threshold': self.low_voltage_threshold,
            'created_at': utc_iso(self.created_at) if self.created_at else None,
            'updated_at': utc_iso(self.updated_at) if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Device {self.device_id}>'
