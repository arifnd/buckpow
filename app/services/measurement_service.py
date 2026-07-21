from datetime import datetime, timezone

from sqlalchemy.orm import Session as DBSession, selectinload

from app.models import Measurement
from app.models.session import Session as SessionModel
from app.utils.calculations import calc_load_voltage, calc_energy_increment
from app.utils.dates import utc_iso
from app.utils.pagination import PaginatedResult
from app.services.device_service import DeviceService
from app.services.session_service import SessionService
from app.services.alert_service import AlertService


class MeasurementService:

    @staticmethod
    def create(db: DBSession, device_id_str, bus_voltage, shunt_voltage=0.0, current=0.0, power=0.0):
        device = DeviceService.get_or_create(db, device_id_str)
        DeviceService.touch(db, device_id_str)

        load_voltage = calc_load_voltage(bus_voltage, shunt_voltage)
        power_w = power / 1000.0
        current_a = current / 1000.0

        session = SessionService.get_active_session(db, device.id)
        session_id = session.id if session else None

        last = db.query(Measurement).filter_by(device_id=device.id).order_by(
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
        db.add(measurement)
        db.commit()

        AlertService.generate_alerts(db, device, bus_voltage, current_a, power_w)

        return measurement

    @staticmethod
    def get_recent(db: DBSession, limit=50, device_id=None):
        q = db.query(Measurement)
        if device_id:
            q = q.filter_by(device_id=device_id)
        return q.order_by(Measurement.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_chart_data(db: DBSession, limit=500, device_id=None, session_id=None, granularity=None,
                       start_date=None, end_date=None):
        q = db.query(Measurement)
        if device_id:
            q = q.filter_by(device_id=device_id)
        if session_id:
            q = q.filter_by(session_id=session_id)
        if start_date:
            q = q.filter(Measurement.created_at >= start_date)
        if end_date:
            q = q.filter(Measurement.created_at <= end_date)

        if granularity and granularity in ('s', 'm', 'h', 'd'):
            rows = q.order_by(Measurement.created_at.asc()).all()
            buckets = {}
            for m in rows:
                ts = m.created_at
                if granularity == 's':
                    key = ts.replace(second=ts.second, microsecond=0).isoformat()
                elif granularity == 'm':
                    key = ts.replace(minute=ts.minute, second=0, microsecond=0).isoformat()
                elif granularity == 'h':
                    key = ts.replace(hour=ts.hour, minute=0, second=0, microsecond=0).isoformat()
                else:
                    key = ts.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
                if key not in buckets:
                    buckets[key] = {'voltage': [], 'load_voltage': [], 'current': [], 'power': [], 'energy': []}
                buckets[key]['voltage'].append(m.bus_voltage)
                buckets[key]['load_voltage'].append(m.load_voltage)
                buckets[key]['current'].append(m.current)
                buckets[key]['power'].append(m.power)
                buckets[key]['energy'].append(m.energy)
            labels = []
            voltage = []
            load_voltage = []
            current = []
            power = []
            energy = []
            keys = sorted(buckets.keys())[-limit:] if len(buckets) > limit else sorted(buckets.keys())
            for k in keys:
                b = buckets[k]
                labels.append(k + 'Z')
                voltage.append(round(sum(b['voltage']) / len(b['voltage']), 3))
                load_voltage.append(round(sum(b['load_voltage']) / len(b['load_voltage']), 3))
                current.append(round(sum(b['current']) / len(b['current']), 3))
                power.append(round(sum(b['power']) / len(b['power']), 3))
                energy.append(round(b['energy'][-1], 6))
            return {
                'labels': labels,
                'voltage': voltage,
                'load_voltage': load_voltage,
                'current': current,
                'power': power,
                'energy': energy,
            }

        rows = q.order_by(Measurement.created_at.desc()).limit(limit).all()
        rows.reverse()
        return {
            'labels': [utc_iso(r.created_at) if r.created_at else '' for r in rows],
            'voltage': [r.bus_voltage for r in rows],
            'load_voltage': [r.load_voltage for r in rows],
            'current': [r.current for r in rows],
            'power': [r.power for r in rows],
            'energy': [r.energy for r in rows],
        }

    @staticmethod
    def get_stats(db: DBSession, device_id=None):
        q = db.query(Measurement)
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
    def get_session_stats(db: DBSession, session_id):
        session = db.query(SessionModel).options(selectinload(SessionModel.device_ref)).filter(SessionModel.id == session_id).first()
        if not session:
            return None

        measurements = db.query(Measurement).filter_by(session_id=session_id).order_by(
            Measurement.created_at.asc()
        ).all()

        if not measurements:
            return {
                'session_id': session.id,
                'session_name': session.name,
                'device_name': session.device_ref.alias or session.device_ref.device_id if session.device_ref else None,
                'avg_power': 0,
                'peak_power': 0,
                'total_energy': 0,
                'avg_current': 0,
                'voltage_stddev': 0,
                'duration': 0,
                'measurement_count': 0,
                'started_at': utc_iso(session.started_at) if session.started_at else None,
                'ended_at': utc_iso(session.ended_at) if session.ended_at else None,
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
        started_at = session.started_at
        ended_at = session.ended_at
        if started_at and started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=timezone.utc)
        if ended_at and ended_at.tzinfo is None:
            ended_at = ended_at.replace(tzinfo=timezone.utc)
        if started_at and ended_at:
            duration = (ended_at - started_at).total_seconds()
        elif started_at:
            duration = (datetime.now(timezone.utc) - started_at).total_seconds()

        return {
            'session_id': session.id,
            'session_name': session.name,
            'device_name': session.device_ref.alias or session.device_ref.device_id if session.device_ref else None,
            'avg_power': round(avg_power, 3),
            'peak_power': round(peak_power, 3),
            'total_energy': round(total_energy, 6),
            'avg_current': round(avg_current, 3),
            'voltage_stddev': round(voltage_stddev, 6),
            'duration': round(duration, 1),
            'measurement_count': n,
            'started_at': utc_iso(session.started_at) if session.started_at else None,
            'ended_at': utc_iso(session.ended_at) if session.ended_at else None,
        }

    @staticmethod
    def get_paginated(db: DBSession, page=1, per_page=50, device_id=None, session_id=None, start_date=None, end_date=None):
        q = db.query(Measurement)
        if device_id:
            q = q.filter_by(device_id=device_id)
        if session_id:
            q = q.filter_by(session_id=session_id)
        if start_date:
            q = q.filter(Measurement.created_at >= start_date)
        if end_date:
            q = q.filter(Measurement.created_at <= end_date)
        q = q.order_by(Measurement.created_at.desc())
        offset = (page - 1) * per_page
        total = q.count()
        items = q.offset(offset).limit(per_page).all()
        pages = (total + per_page - 1) // per_page if total > 0 else 1
        return PaginatedResult(items=items, page=page, pages=pages, total=total, per_page=per_page)

    @staticmethod
    def get_all_filtered(db: DBSession, device_id=None, session_id=None, start_date=None, end_date=None):
        q = db.query(Measurement)
        if device_id:
            q = q.filter_by(device_id=device_id)
        if session_id:
            q = q.filter_by(session_id=session_id)
        if start_date:
            q = q.filter(Measurement.created_at >= start_date)
        if end_date:
            q = q.filter(Measurement.created_at <= end_date)
        return q.order_by(Measurement.created_at.asc()).all()
