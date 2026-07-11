from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    description = Column(Text, default='')
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship('User', backref='projects', lazy='select')
    devices = relationship('Device', backref='project', lazy='dynamic')
    sessions = relationship('Session', backref='project', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id,
            'owner_name': self.owner.name if self.owner else None,
            'device_count': self.devices.count() if hasattr(self, 'devices') else 0,
            'session_count': self.sessions.count() if hasattr(self, 'sessions') else 0,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Project {self.name}>'
