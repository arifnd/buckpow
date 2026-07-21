from datetime import datetime, timezone, timedelta

from datetime import datetime, timezone, timedelta

from src.database import SessionLocal
from src.models import Device, Session, Measurement, User, Project, Alert
from src.auth.service import UserService
from src.devices.service import DeviceService
from src.sessions.service import SessionService
from src.measurements.service import MeasurementService
from src.alerts.service import AlertService
from src.projects.service import ProjectService
from src.dashboard.service import DashboardService


class TestDashboardService:

    def _db(self, app):

        return SessionLocal()



    def test_get_summary_empty(self, app):

        db = self._db(app)

        summary = DashboardService(db).get_summary()

        assert summary['online_devices'] == 0

        assert summary['offline_devices'] == 0

        assert summary['total_projects'] == 0

        assert summary['active_sessions'] == 0

        assert summary['today_energy'] == 0

        assert summary['current_power'] == 0

        db.close()



    def test_get_summary_with_data(self, app):

        db = self._db(app)

        d = DeviceService(db).create('esp32-dash')

        d.last_seen = datetime.now(timezone.utc)

        s = SessionService(db).create(d.id, 'Dash Sess')

        SessionService(db).start(s.id)

        MeasurementService(db).create('esp32-dash', bus_voltage=5.0,

                                  shunt_voltage=80.0, current=200, power=1000)

        summary = DashboardService(db).get_summary()

        assert summary['online_devices'] >= 1

        assert summary['active_sessions'] >= 1

        assert summary['current_power'] > 0

        db.close()



    def test_get_statistics_empty(self, app):

        db = self._db(app)

        stats = DashboardService(db).get_statistics()

        assert stats['energy']['hourly'] == []

        assert stats['energy']['daily'] == []

        db.close()



    def test_get_statistics_with_data(self, app):

        db = self._db(app)

        MeasurementService(db).create('esp32-dash-stats', bus_voltage=5.0,

                                  shunt_voltage=80.0, current=200, power=1000)

        stats = DashboardService(db).get_statistics()

        assert stats['voltage']['avg'] > 0

        db.close()



    def test_get_statistics_with_device_filter(self, app):

        db = self._db(app)

        d = DeviceService(db).create('esp32-filter-dev')

        MeasurementService(db).create('esp32-filter-dev', bus_voltage=5.0,

                                  shunt_voltage=80.0, current=200, power=1000)

        stats = DashboardService(db).get_statistics(device_id=d.id)

        assert stats['voltage']['avg'] > 0

        db.close()



    def test_get_statistics_with_session_filter(self, app):

        db = self._db(app)

        d = DeviceService(db).create('esp32-filter-sess')

        s = SessionService(db).create(d.id, 'Filter Sess')

        SessionService(db).start(s.id)

        MeasurementService(db).create('esp32-filter-sess', bus_voltage=5.0,

                                  shunt_voltage=80.0, current=200, power=1000)

        stats = DashboardService(db).get_statistics(session_id=s.id)

        assert stats['voltage']['avg'] > 0

        assert stats['session_started_at'] is not None

        db.close()



    def test_get_statistics_with_date_filter(self, app):

        db = self._db(app)

        MeasurementService(db).create('esp32-filter-date', bus_voltage=5.0,

                                  shunt_voltage=80.0, current=200, power=1000)

        from datetime import datetime, timezone, timedelta

        start = datetime.now(timezone.utc) - timedelta(hours=1)

        end = datetime.now(timezone.utc) + timedelta(hours=1)

        stats = DashboardService(db).get_statistics(start_date=start, end_date=end)

        assert stats['voltage']['avg'] > 0

        db.close()



    def test_get_statistics_outside_date_range(self, app):

        db = self._db(app)

        MeasurementService(db).create('esp32-filter-date2', bus_voltage=5.0,

                                  shunt_voltage=80.0, current=200, power=1000)

        from datetime import datetime, timezone, timedelta

        start = datetime.now(timezone.utc) + timedelta(hours=10)

        end = datetime.now(timezone.utc) + timedelta(hours=11)

        stats = DashboardService(db).get_statistics(start_date=start, end_date=end)

        assert stats['voltage']['avg'] == 0

        db.close()



    def test_get_energy_breakdown_with_device_filter(self, app):

        db = self._db(app)

        d = DeviceService(db).create('esp32-energy-filter')

        MeasurementService(db).create('esp32-energy-filter', bus_voltage=5.0,

                                  shunt_voltage=80.0, current=200, power=1000)

        energy = DashboardService(db)._get_energy_breakdown(device_id=d.id)

        assert 'hourly' in energy

        db.close()



    def test_get_energy_breakdown_empty(self, app):

        db = self._db(app)

        energy = DashboardService(db)._get_energy_breakdown()

        assert energy == {'hourly': [], 'daily': [], 'weekly': [], 'monthly': []}

        db.close()



    def test_get_energy_breakdown_session_boundary(self, app):

        db = self._db(app)

        d1 = DeviceService(db).create('esp32-boundary1')

        d2 = DeviceService(db).create('esp32-boundary2')

        sess1 = SessionService(db).create(d1.id, 'Boundary S1')

        sess2 = SessionService(db).create(d2.id, 'Boundary S2')

        from src.models import Measurement as M

        from datetime import datetime, timezone, timedelta

        now = datetime.now(timezone.utc)

        m1 = M(device_id=d1.id, session_id=sess1.id, bus_voltage=5.0,

                shunt_voltage=0.0, load_voltage=5.0, current=0.1, power=0.5, energy=1.0,

                created_at=now - timedelta(minutes=5))

        m2 = M(device_id=d2.id, session_id=sess2.id, bus_voltage=5.0,

                shunt_voltage=0.0, load_voltage=5.0, current=0.1, power=0.5, energy=2.0,

                created_at=now)

        db.add_all([m1, m2])

        db.commit()

        energy = DashboardService(db)._get_energy_breakdown()

        assert isinstance(energy['hourly'], list)

        assert isinstance(energy['daily'], list)

        db.close()

