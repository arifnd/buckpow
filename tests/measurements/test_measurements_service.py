


from src.database import SessionLocal
from src.devices.service import DeviceService
from src.measurements.service import MeasurementService
from src.sessions.service import SessionService


class TestMeasurementService:

    def _db(self, app):

        return SessionLocal()



    def test_create_measurement(self, app):

        db = self._db(app)

        m = MeasurementService(db).create('esp32-meas-svc', bus_voltage=5.0,

                                      shunt_voltage=80.0, current=200, power=1000)

        assert m.id is not None

        assert m.load_voltage == 5.08

        assert m.current == 0.2

        assert m.power == 1.0

        db.close()



    def test_create_auto_registers_device(self, app):

        db = self._db(app)

        m = MeasurementService(db).create('esp32-auto-reg', bus_voltage=5.0,

                                      shunt_voltage=80.0, current=200, power=1000)

        device = DeviceService(db).get_by_device_id('esp32-auto-reg')

        assert device is not None

        assert m.device_id == device.id

        db.close()



    def test_create_with_session(self, app):

        db = self._db(app)

        d = DeviceService(db).create('esp32-sess-m')

        s = SessionService(db).create(d.id, 'Meas Session')

        SessionService(db).start(s.id)

        m = MeasurementService(db).create('esp32-sess-m', bus_voltage=5.0,

                                      shunt_voltage=80.0, current=200, power=1000)

        assert m.session_id == s.id

        db.close()



    def test_energy_accumulation_same_session(self, app):

        db = self._db(app)

        d = DeviceService(db).create('esp32-energy')

        s = SessionService(db).create(d.id, 'Energy')

        SessionService(db).start(s.id)

        m1 = MeasurementService(db).create('esp32-energy', bus_voltage=5.0,

                                       shunt_voltage=80.0, current=200, power=1000)

        m2 = MeasurementService(db).create('esp32-energy', bus_voltage=5.0,

                                       shunt_voltage=80.0, current=200, power=1000)

        assert m2.energy > m1.energy

        db.close()



    def test_energy_no_session_starts_at_zero(self, app):

        db = self._db(app)

        m = MeasurementService(db).create('esp32-no-sess', bus_voltage=5.0,

                                      shunt_voltage=80.0, current=200, power=1000)

        assert m.energy == 0.0

        db.close()



    def test_get_recent(self, app):

        db = self._db(app)

        MeasurementService(db).create('esp32-recent', bus_voltage=5.0,

                                  shunt_voltage=80.0, current=200, power=1000)

        recent = MeasurementService(db).get_recent(limit=10)

        assert len(recent) >= 1

        db.close()



    def test_get_stats_empty(self, app):

        db = self._db(app)

        stats = MeasurementService(db).get_stats()

        assert stats['energy']['total'] == 0

        db.close()



    def test_get_stats_with_data(self, app):

        db = self._db(app)

        MeasurementService(db).create('esp32-stats', bus_voltage=5.0,

                                  shunt_voltage=80.0, current=200, power=1000)

        stats = MeasurementService(db).get_stats()

        assert stats['voltage']['avg'] > 0

        db.close()



    def test_get_chart_data_no_granularity(self, app):

        db = self._db(app)

        MeasurementService(db).create('esp32-chart-svc', bus_voltage=5.0,

                                  shunt_voltage=80.0, current=200, power=1000)

        data = MeasurementService(db).get_chart_data(limit=10)

        assert len(data['labels']) >= 1

        db.close()



    def test_get_chart_data_with_granularity_hour(self, app):

        db = self._db(app)

        MeasurementService(db).create('esp32-gran', bus_voltage=5.0,

                                  shunt_voltage=80.0, current=200, power=1000)

        data = MeasurementService(db).get_chart_data(limit=10, granularity='h')

        assert len(data['labels']) >= 1

        db.close()



    def test_get_session_stats_empty(self, app):

        db = self._db(app)

        d = DeviceService(db).create('esp32-ss-empty')

        s = SessionService(db).create(d.id, 'Empty Session')

        stats = MeasurementService.get_session_stats(db, s.id)

        assert stats is not None

        assert stats['measurement_count'] == 0

        db.close()



    def test_get_session_stats_with_data(self, app):

        db = self._db(app)

        d = DeviceService(db).create('esp32-ss-data')

        s = SessionService(db).create(d.id, 'Data Session')

        SessionService(db).start(s.id)

        MeasurementService(db).create('esp32-ss-data', bus_voltage=5.0,

                                  shunt_voltage=80.0, current=200, power=1000)

        stats = MeasurementService.get_session_stats(db, s.id)

        assert stats['measurement_count'] == 1

        assert stats['avg_power'] > 0

        db.close()



    def test_get_session_stats_nonexistent(self, app):

        db = self._db(app)

        stats = MeasurementService.get_session_stats(db, 99999)

        assert stats is None

        db.close()



    def test_get_paginated(self, app):

        db = self._db(app)

        for i in range(3):

            MeasurementService(db).create(f'esp32-pag-{i}', bus_voltage=5.0,

                                      shunt_voltage=80.0, current=200, power=1000)

        p = MeasurementService(db).get_paginated(page=1, per_page=2)

        assert len(p.items) == 2

        db.close()



    def test_get_all_filtered(self, app):

        db = self._db(app)

        MeasurementService(db).create('esp32-filt', bus_voltage=5.0,

                                  shunt_voltage=80.0, current=200, power=1000)

        rows = MeasurementService(db).get_all_filtered()

        assert len(rows) >= 1

        db.close()



    def test_get_recent_with_device_filter(self, app):

        db = self._db(app)

        d = DeviceService(db).create('esp32-rec-filt')

        MeasurementService(db).create('esp32-rec-filt', bus_voltage=5.0,

                                  shunt_voltage=80.0, current=200, power=1000)

        recent = MeasurementService(db).get_recent(limit=10, device_id=d.id)

        assert len(recent) >= 1

        db.close()



    def test_get_chart_data_granularity_second(self, app):

        db = self._db(app)

        MeasurementService(db).create('esp32-g-s', bus_voltage=5.0,

                                  shunt_voltage=80.0, current=200, power=1000)

        data = MeasurementService(db).get_chart_data(limit=10, granularity='s')

        assert len(data['labels']) >= 1

        db.close()



    def test_get_chart_data_granularity_minute(self, app):

        db = self._db(app)

        MeasurementService(db).create('esp32-g-m', bus_voltage=5.0,

                                  shunt_voltage=80.0, current=200, power=1000)

        data = MeasurementService(db).get_chart_data(limit=10, granularity='m')

        assert len(data['labels']) >= 1

        db.close()



    def test_get_chart_data_granularity_day(self, app):

        db = self._db(app)

        MeasurementService(db).create('esp32-g-d', bus_voltage=5.0,

                                  shunt_voltage=80.0, current=200, power=1000)

        data = MeasurementService(db).get_chart_data(limit=10, granularity='d')

        assert len(data['labels']) >= 1

        db.close()



    def test_get_chart_data_device_filter(self, app):

        db = self._db(app)

        d = DeviceService(db).create('esp32-cd-filt')

        MeasurementService(db).create('esp32-cd-filt', bus_voltage=5.0,

                                  shunt_voltage=80.0, current=200, power=1000)

        data = MeasurementService(db).get_chart_data(limit=10, device_id=d.id)

        assert len(data['labels']) >= 1

        db.close()



    def test_get_chart_data_session_filter(self, app):

        db = self._db(app)

        d = DeviceService(db).create('esp32-cs-filt')

        s = SessionService(db).create(d.id, 'Chart Session')

        SessionService(db).start(s.id)

        MeasurementService(db).create('esp32-cs-filt', bus_voltage=5.0,

                                  shunt_voltage=80.0, current=200, power=1000)

        data = MeasurementService(db).get_chart_data(limit=10, session_id=s.id)

        assert len(data['labels']) >= 1

        db.close()



    def test_get_stats_device_filter(self, app):

        db = self._db(app)

        d = DeviceService(db).create('esp32-stats-filt')

        MeasurementService(db).create('esp32-stats-filt', bus_voltage=5.0,

                                  shunt_voltage=80.0, current=200, power=1000)

        stats = MeasurementService(db).get_stats(device_id=d.id)

        assert stats['voltage']['avg'] > 0

        db.close()



    def test_energy_no_session_existing_device(self, app):

        db = self._db(app)

        DeviceService(db).create('esp32-ens-exist')

        m1 = MeasurementService(db).create('esp32-ens-exist', bus_voltage=5.0,

                                       shunt_voltage=80.0, current=200, power=1000)

        m2 = MeasurementService(db).create('esp32-ens-exist', bus_voltage=5.0,

                                       shunt_voltage=80.0, current=200, power=1000)

        assert m2.energy > m1.energy

        db.close()



    def test_pzem_create_no_shunt(self, app):

        db = self._db(app)

        m = MeasurementService(db).create('pzem-svc', bus_voltage=230.5,

                                      shunt_voltage=0.0, current=4500, power=1035000)

        assert m.bus_voltage == 230.5

        assert m.shunt_voltage == 0.0

        assert m.load_voltage == 230.5

        assert m.current == 4.5

        assert m.power == 1035.0

        db.close()



    def test_pzem_create_default_shunt(self, app):

        db = self._db(app)

        m = MeasurementService(db).create('pzem-default', bus_voltage=220.0,

                                      current=10000, power=2200000)

        assert m.shunt_voltage == 0.0

        assert m.load_voltage == 220.0

        db.close()



    def test_pzem_energy_accumulation(self, app):

        db = self._db(app)

        DeviceService(db).create('pzem-energy')

        m1 = MeasurementService(db).create('pzem-energy', bus_voltage=230.0,

                                       current=5000, power=1150000)

        m2 = MeasurementService(db).create('pzem-energy', bus_voltage=230.0,

                                       current=5000, power=1150000)

        assert m2.energy > m1.energy

        db.close()



    def test_pzem_chart_data(self, app):

        db = self._db(app)

        MeasurementService(db).create('pzem-chart', bus_voltage=230.0,

                                  current=5000, power=1150000)

        data = MeasurementService(db).get_chart_data(limit=10)

        assert len(data['labels']) >= 1

        assert data['voltage'][0] == 230.0

        db.close()



    def test_pzem_stats(self, app):

        db = self._db(app)

        MeasurementService(db).create('pzem-stats', bus_voltage=230.0,

                                  current=5000, power=1150000)

        stats = MeasurementService(db).get_stats()

        assert stats['voltage']['avg'] == 230.0

        db.close()





