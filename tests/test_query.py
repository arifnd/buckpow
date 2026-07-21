from src.database import SessionLocal
from src.models import Device, Alert
from src.utils.query import FilterBuilder
from src.utils.pagination import PaginatedResult


class TestFilterBuilder:

    def _device(self, db, device_id='esp32-fb'):
        from src.devices.service import DeviceService
        return DeviceService(db).create(device_id)

    def test_eq_filters_by_attribute(self, app):
        db = SessionLocal()
        self._device(db, 'esp32-fb-a')
        self._device(db, 'esp32-fb-b')
        fb = FilterBuilder(Device, db.query(Device))
        fb.eq(device_id='esp32-fb-a')
        assert fb.query.count() == 1
        assert fb.query.first().device_id == 'esp32-fb-a'
        db.close()

    def test_eq_skips_none(self, app):
        db = SessionLocal()
        self._device(db, 'esp32-fb-skip')
        fb = FilterBuilder(Device, db.query(Device))
        fb.eq(device_id=None, alias=None)
        assert fb.query.count() >= 1
        db.close()

    def test_eq_multiple_filters(self, app):
        db = SessionLocal()
        d = self._device(db, 'esp32-fb-multi')
        d.alias = 'Multi Filter'
        db.commit()
        fb = FilterBuilder(Device, db.query(Device))
        fb.eq(device_id='esp32-fb-multi', alias='Multi Filter')
        assert fb.query.count() == 1
        db.close()

    def test_date_range_start_only(self, app):
        from datetime import datetime, timezone, timedelta
        from src.models import Measurement
        db = SessionLocal()
        from src.measurements.service import MeasurementService
        ms = MeasurementService(db)
        ms.create('esp32-dr-s', bus_voltage=5.0, shunt_voltage=80, current=200, power=1000)
        future = datetime.now(timezone.utc) + timedelta(days=365)
        fb = FilterBuilder(Measurement, db.query(Measurement))
        fb.date_range('created_at', start=future)
        assert fb.query.count() == 0
        db.close()

    def test_date_range_end_only(self, app):
        from datetime import datetime, timezone, timedelta
        from src.models import Measurement
        db = SessionLocal()
        from src.measurements.service import MeasurementService
        ms = MeasurementService(db)
        ms.create('esp32-dr-e', bus_voltage=5.0, shunt_voltage=80, current=200, power=1000)
        past = datetime.now(timezone.utc) - timedelta(days=365)
        fb = FilterBuilder(Measurement, db.query(Measurement))
        fb.date_range('created_at', end=past)
        assert fb.query.count() == 0
        db.close()

    def test_date_range_both(self, app):
        from datetime import datetime, timezone, timedelta
        from src.models import Measurement
        db = SessionLocal()
        from src.measurements.service import MeasurementService
        ms = MeasurementService(db)
        ms.create('esp32-dr-b', bus_voltage=5.0, shunt_voltage=80, current=200, power=1000)
        past = datetime.now(timezone.utc) - timedelta(days=1)
        future = datetime.now(timezone.utc) + timedelta(days=1)
        fb = FilterBuilder(Measurement, db.query(Measurement))
        fb.date_range('created_at', start=past, end=future)
        assert fb.query.count() >= 1
        db.close()

    def test_is_null_false(self, app):
        db = SessionLocal()
        self._device(db, 'esp32-fb-null')
        fb = FilterBuilder(Device, db.query(Device))
        fb.is_null('alias', is_null=False)
        assert fb.query.count() >= 1
        db.close()

    def test_is_null_true(self, app):
        from src.alerts.models import Alert
        db = SessionLocal()
        alert = Alert(device_id=0, level='info', message='test', resolved_at=None)
        db.add(alert)
        db.commit()
        fb = FilterBuilder(Alert, db.query(Alert))
        fb.is_null('resolved_at', is_null=True)
        assert fb.query.count() >= 1
        db.close()

    def test_order_asc(self, app):
        db = SessionLocal()
        self._device(db, 'esp32-fb-ord-b')
        self._device(db, 'esp32-fb-ord-a')
        fb = FilterBuilder(Device, db.query(Device))
        fb.order('device_id', desc=False)
        results = fb.query.all()
        assert results[0].device_id <= results[-1].device_id
        db.close()

    def test_order_desc(self, app):
        db = SessionLocal()
        self._device(db, 'esp32-fb-od-b')
        self._device(db, 'esp32-fb-od-a')
        fb = FilterBuilder(Device, db.query(Device))
        fb.order('device_id', desc=True)
        results = fb.query.limit(2).all()
        assert results[0].device_id >= results[-1].device_id
        db.close()

    def test_limit(self, app):
        db = SessionLocal()
        self._device(db, 'esp32-fb-lim-1')
        self._device(db, 'esp32-fb-lim-2')
        fb = FilterBuilder(Device, db.query(Device))
        fb.limit(1)
        assert len(fb.query.all()) == 1
        db.close()

    def test_paginate_returns_paginated_result(self, app):
        db = SessionLocal()
        for i in range(5):
            self._device(db, f'esp32-fb-pg-{i}')
        fb = FilterBuilder(Device, db.query(Device))
        result = fb.paginate(page=1, per_page=2)
        assert isinstance(result, PaginatedResult)
        assert len(result.items) == 2
        assert result.total == 5
        assert result.pages == 3
        assert result.page == 1
        assert result.per_page == 2
        db.close()

    def test_chaining(self, app):
        db = SessionLocal()
        self._device(db, 'esp32-fb-chain')
        fb = FilterBuilder(Device, db.query(Device))
        fb.eq(device_id='esp32-fb-chain').order('device_id').limit(10)
        assert fb.query.count() == 1
        db.close()
