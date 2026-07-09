from datetime import datetime, timezone

from app import db


class Alert(db.Model):
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False, index=True)
    level = db.Column(db.String(16), nullable=False, default='warning')
    message = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    resolved_at = db.Column(db.DateTime, nullable=True)

    device_rel = db.relationship('Device', backref='alerts', lazy='select')

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
