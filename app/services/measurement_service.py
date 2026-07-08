from datetime import datetime

from app import db
from app.models import Measurement
from app.utils.calculations import calc_load_voltage, calc_energy_increment
from app.services.device_service import DeviceService
from app.services.session_service import SessionService


class MeasurementService:

    @staticmethod
    def create(device_id_str, bus_voltage, shunt_voltage=0.0, current=0.0, power=0.0):
        device = DeviceService.get_or_create(device_id_str)
        DeviceService.touch(device_id_str)

        load_voltage = calc_load_voltage(bus_voltage, shunt_voltage)
        power_w = power / 1000.0
        current_a = current / 1000.0

        session = SessionService.get_active_session(device.id)
        session_id = session.id if session else None

        last = Measurement.query.filter_by(device_id=device.id).order_by(
            Measurement.created_at.desc()
        ).first()

        if last:
            energy = last.energy + calc_energy_increment(
                power_w, device.sampling_interval
            )
        else:
            energy = 0.0

        measurement = Measurement(
            session_id=session_id,
            device_id=device.id,
            bus_voltage=bus_voltage,
            shunt_voltage=shunt_voltage,
            load_voltage=load_voltage,
            current=current_a,
            power=power_w,
            energy=energy,
        )
        db.session.add(measurement)
        db.session.commit()
        return measurement

    @staticmethod
    def get_recent(limit=50, device_id=None):
        q = Measurement.query
        if device_id:
            q = q.filter_by(device_id=device_id)
        return q.order_by(Measurement.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_chart_data(limit=100, device_id=None, session_id=None):
        q = Measurement.query
        if device_id:
            q = q.filter_by(device_id=device_id)
        if session_id:
            q = q.filter_by(session_id=session_id)
        rows = q.order_by(Measurement.created_at.desc()).limit(limit).all()
        rows.reverse()
        return {
            'labels': [r.created_at.isoformat() + 'Z' if r.created_at else '' for r in rows],
            'voltage': [r.bus_voltage for r in rows],
            'load_voltage': [r.load_voltage for r in rows],
            'current': [r.current for r in rows],
            'power': [r.power for r in rows],
            'energy': [r.energy for r in rows],
        }

    @staticmethod
    def get_stats(device_id=None):
        q = Measurement.query
        if device_id:
            q = q.filter_by(device_id=device_id)

        rows = q.order_by(Measurement.created_at.desc()).limit(500).all()

        if not rows:
            return {
                'voltage': {'min': 0, 'max': 0, 'avg': 0},
                'current': {'min': 0, 'max': 0, 'avg': 0},
                'power': {'min': 0, 'max': 0, 'avg': 0, 'peak': 0},
                'energy': {'total': 0},
            }

        voltages = [r.bus_voltage for r in rows]
        currents = [r.current for r in rows]
        powers = [r.power for r in rows]

        return {
            'voltage': {
                'min': round(min(voltages), 3),
                'max': round(max(voltages), 3),
                'avg': round(sum(voltages) / len(voltages), 3),
            },
            'current': {
                'min': round(min(currents), 3),
                'max': round(max(currents), 3),
                'avg': round(sum(currents) / len(currents), 3),
            },
            'power': {
                'min': round(min(powers), 3),
                'max': round(max(powers), 3),
                'avg': round(sum(powers) / len(powers), 3),
                'peak': round(max(powers), 3),
            },
            'energy': {
                'total': round(rows[0].energy, 6) if rows else 0,
            },
        }

    @staticmethod
    def get_paginated(page=1, per_page=50, device_id=None, start_date=None, end_date=None):
        q = Measurement.query
        if device_id:
            q = q.filter_by(device_id=device_id)
        if start_date:
            q = q.filter(Measurement.created_at >= start_date)
        if end_date:
            q = q.filter(Measurement.created_at <= end_date)
        q = q.order_by(Measurement.created_at.desc())
        return q.paginate(page=page, per_page=per_page, error_out=False)
