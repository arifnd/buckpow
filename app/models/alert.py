from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Alert(Base):
    __tablename__ = 'alerts'

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('devices.id'), nullable=False, index=True)
    level = Column(String(16), nullable=False, default='warning')
    message = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)

    device_rel = relationship('Device', backref='alerts', lazy='select')

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'device_name': self.device_rel.device_id if self.device_rel else None,
            'level': self.level,
            'message': self.message,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() + 'Z' if self.resolved_at else None,
        }

    def __repr__(self):
        return f'<Alert {self.level}: {self.message[:40]}>'
