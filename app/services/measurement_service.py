from datetime import datetime, timezone

from sqlalchemy import func

from app import db
from app.models import Measurement, Session
from app.utils.calculations import calc_load_voltage, calc_energy_increment
from app.services.device_service import DeviceService
from app.services.session_service import SessionService
from app.services.alert_service import AlertService


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

        inc = calc_energy_increment(power_w, device.sampling_interval)

        if last and session_id and last.session_id == session_id:
            energy = last.energy + inc
        elif last and not session_id:
            energy = last.energy + inc
        else:
            energy = inc if session_id else 0.0

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

        AlertService.generate_alerts(device, bus_voltage, current_a, power_w)

        return measurement

    @staticmethod
    def get_recent(limit=50, device_id=None):
        q = Measurement.query
        if device_id:
            q = q.filter_by(device_id=device_id)
        return q.order_by(Measurement.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_chart_data(limit=500, device_id=None, session_id=None, granularity=None,
                       start_date=None, end_date=None):
        q = Measurement.query
        if device_id:
            q = q.filter_by(device_id=device_id)
        if session_id:
            q = q.filter_by(session_id=session_id)
        if start_date:
            q = q.filter(Measurement.created_at >= start_date)
        if end_date:
            q = q.filter(Measurement.created_at <= end_date)

        if granularity and granularity in ('s', 'm', 'h', 'd'):
            fmt_map = {
                's': '%Y-%m-%dT%H:%M:%S',
                'm': '%Y-%m-%dT%H:%M:00',
                'h': '%Y-%m-%dT%H:00:00',
                'd': '%Y-%m-%d',
            }
            bucket = func.strftime(fmt_map[granularity], Measurement.created_at)
            rows = q.with_entities(
                bucket.label('tb'),
                func.avg(Measurement.bus_voltage).label('avg_voltage'),
                func.avg(Measurement.load_voltage).label('avg_load_voltage'),
                func.avg(Measurement.current).label('avg_current'),
                func.avg(Measurement.power).label('avg_power'),
                func.avg(Measurement.energy).label('avg_energy'),
            ).group_by('tb').order_by(func.max(Measurement.created_at).desc()).limit(limit).all()
            rows.reverse()
            return {
                'labels': [r.tb + 'Z' for r in rows],
                'voltage': [round(r.avg_voltage, 3) for r in rows],
                'load_voltage': [round(r.avg_load_voltage, 3) for r in rows],
                'current': [round(r.avg_current, 3) for r in rows],
                'power': [round(r.avg_power, 3) for r in rows],
                'energy': [round(r.avg_energy, 3) for r in rows],
            }

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
    def get_session_stats(session_id):
        session = db.session.get(Session, session_id)
        if not session:
            return None

        measurements = Measurement.query.filter_by(session_id=session_id).order_by(
            Measurement.created_at.asc()
        ).all()

        if not measurements:
            return {
                'session_id': session.id,
                'session_name': session.name,
                'device_name': session.device.alias or session.device.device_id if session.device else None,
                'avg_power': 0,
                'peak_power': 0,
                'total_energy': 0,
                'avg_current': 0,
                'voltage_stddev': 0,
                'duration': 0,
                'measurement_count': 0,
                'started_at': session.started_at.isoformat() + 'Z' if session.started_at else None,
                'ended_at': session.ended_at.isoformat() + 'Z' if session.ended_at else None,
                'chart_data': {'labels': [], 'power': [], 'voltage': [], 'current': []},
            }

        powers = [m.power for m in measurements]
        currents = [m.current for m in measurements]
        voltages = [m.bus_voltage for m in measurements]
        n = len(measurements)

        avg_power = sum(powers) / n
        peak_power = max(powers)
        avg_current = sum(currents) / n
        total_energy = measurements[-1].energy if measurements else 0

        avg_voltage = sum(voltages) / n
        variance = sum((v - avg_voltage) ** 2 for v in voltages) / n
        voltage_stddev = variance ** 0.5

        duration = 0
        if session.started_at and session.ended_at:
            duration = (session.ended_at - session.started_at).total_seconds()
        elif session.started_at:
            duration = (datetime.now(timezone.utc) - session.started_at).total_seconds()

        return {
            'session_id': session.id,
            'session_name': session.name,
            'device_name': session.device.alias or session.device.device_id if session.device else None,
            'avg_power': round(avg_power, 3),
            'peak_power': round(peak_power, 3),
            'total_energy': round(total_energy, 6),
            'avg_current': round(avg_current, 3),
            'voltage_stddev': round(voltage_stddev, 6),
            'duration': round(duration, 1),
            'measurement_count': n,
            'started_at': session.started_at.isoformat() + 'Z' if session.started_at else None,
            'ended_at': session.ended_at.isoformat() + 'Z' if session.ended_at else None,
            'chart_data': {
                'labels': [m.created_at.isoformat() + 'Z' if m.created_at else '' for m in measurements],
                'power': [m.power for m in measurements],
                'voltage': [m.bus_voltage for m in measurements],
                'current': [m.current for m in measurements],
            },
        }

    @staticmethod
    def get_paginated(page=1, per_page=50, device_id=None, session_id=None, start_date=None, end_date=None):
        q = Measurement.query
        if device_id:
            q = q.filter_by(device_id=device_id)
        if session_id:
            q = q.filter_by(session_id=session_id)
        if start_date:
            q = q.filter(Measurement.created_at >= start_date)
        if end_date:
            q = q.filter(Measurement.created_at <= end_date)
        q = q.order_by(Measurement.created_at.desc())
        return q.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_all_filtered(device_id=None, session_id=None, start_date=None, end_date=None):
        q = Measurement.query
        if device_id:
            q = q.filter_by(device_id=device_id)
        if session_id:
            q = q.filter_by(session_id=session_id)
        if start_date:
            q = q.filter(Measurement.created_at >= start_date)
        if end_date:
            q = q.filter(Measurement.created_at <= end_date)
        return q.order_by(Measurement.created_at.asc()).all()
