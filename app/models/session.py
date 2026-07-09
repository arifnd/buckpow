from app import db


class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    name = db.Column(db.String(256), nullable=False)
    target_device = db.Column(db.String(64), default='')
    description = db.Column(db.Text, default='')
    status = db.Column(db.String(16), default='draft')
    started_at = db.Column(db.DateTime, nullable=True)
    ended_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    measurements = db.relationship('Measurement', backref='session', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'device_name': self.device.alias or self.device.device_id if self.device else None,
            'name': self.name,
            'target_device': self.target_device,
            'description': self.description,
            'status': self.status,
            'started_at': self.started_at.isoformat() + 'Z' if self.started_at else None,
            'ended_at': self.ended_at.isoformat() + 'Z' if self.ended_at else None,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Session {self.name}>'
