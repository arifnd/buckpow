from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils.dates import utc_iso


class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    action = Column(String(64), nullable=False)
    target_type = Column(String(32), nullable=True)
    target_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    user = relationship('User', backref='audit_logs', lazy='select')

    __table_args__ = (
        Index('idx_audit_created', 'created_at'),
        Index('idx_audit_action', 'action'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'action': self.action,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': utc_iso(self.created_at) if self.created_at else None,
        }

    def __repr__(self):
        return f'<AuditLog {self.action}>'
