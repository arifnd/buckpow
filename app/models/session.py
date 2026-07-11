from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Session(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('devices.id'), nullable=False)
    name = Column(String(256), nullable=False)
    target_device = Column(String(64), default='')
    description = Column(Text, default='')
    status = Column(String(16), default='draft')
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    device_ref = relationship('Device', back_populates='sessions')
    measurements = relationship('Measurement', back_populates='session_ref', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'device_name': self.device_ref.alias or self.device_ref.device_id if self.device_ref else None,
            'name': self.name,
            'target_device': self.target_device,
            'description': self.description,
            'status': self.status,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'started_at': self.started_at.isoformat() + 'Z' if self.started_at else None,
            'ended_at': self.ended_at.isoformat() + 'Z' if self.ended_at else None,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Session {self.name}>'
