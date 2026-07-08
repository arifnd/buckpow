from app import db


class Measurement(db.Model):
    __tablename__ = 'measurements'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    bus_voltage = db.Column(db.Float, nullable=False)
    shunt_voltage = db.Column(db.Float, default=0.0)
    load_voltage = db.Column(db.Float, nullable=False)
    current = db.Column(db.Float, nullable=False)
    power = db.Column(db.Float, nullable=False)
    energy = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (
        db.Index('idx_measurement_device_time', 'device_id', 'created_at'),
        db.Index('idx_measurement_session_time', 'session_id', 'created_at'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'device_id': self.device_id,
            'bus_voltage': self.bus_voltage,
            'shunt_voltage': self.shunt_voltage,
            'load_voltage': self.load_voltage,
            'current': self.current,
            'power': self.power,
            'energy': self.energy,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
        }

    def __repr__(self):
        return f'<Measurement {self.id} device={self.device_id}>'
