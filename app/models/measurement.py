from datetime import datetime, timezone

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils.dates import utc_iso


class Measurement(Base):
    __tablename__ = 'measurements'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=True)
    device_id = Column(Integer, ForeignKey('devices.id'), nullable=False)
    bus_voltage = Column(Float, nullable=False)
    shunt_voltage = Column(Float, default=0.0)
    load_voltage = Column(Float, nullable=False)
    current = Column(Float, nullable=False)
    power = Column(Float, nullable=False)
    energy = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_measurement_device_time', 'device_id', 'created_at'),
        Index('idx_measurement_session_time', 'session_id', 'created_at'),
    )

    device_ref = relationship('Device', back_populates='measurements')
    session_ref = relationship('Session', back_populates='measurements')

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'session_name': self.session_ref.name if self.session_ref else None,
            'device_id': self.device_id,
            'device_name': self.device_ref.alias or self.device_ref.device_id if self.device_ref else None,
            'bus_voltage': self.bus_voltage,
            'shunt_voltage': self.shunt_voltage,
            'load_voltage': self.load_voltage,
            'current': self.current,
            'power': self.power,
            'energy': self.energy,
            'created_at': utc_iso(self.created_at) if self.created_at else None,
        }

    def __repr__(self):
        return f'<Measurement {self.id} device={self.device_id}>'
