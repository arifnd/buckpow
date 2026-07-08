from app import db


class Device(db.Model):
    __tablename__ = 'devices'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    alias = db.Column(db.String(128), default='')
    description = db.Column(db.Text, default='')
    sampling_interval = db.Column(db.Integer, default=1)
    last_seen = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(16), default='offline')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    sessions = db.relationship('Session', backref='device', lazy='dynamic')
    measurements = db.relationship('Measurement', backref='device', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'alias': self.alias,
            'description': self.description,
            'sampling_interval': self.sampling_interval,
            'last_seen': self.last_seen.isoformat() + 'Z' if self.last_seen else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Device {self.device_id}>'
