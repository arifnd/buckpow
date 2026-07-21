from datetime import datetime, timezone, timedelta

from datetime import datetime, timezone, timedelta


from src.database import SessionLocal


from src.auth.models import User


from src.devices.models import Device


from src.sessions.models import Session


from src.measurements.models import Measurement


from src.projects.models import Project

from src.alerts.models import Alert
from src.auth.service import UserService
from src.devices.service import DeviceService
from src.sessions.service import SessionService
from src.measurements.service import MeasurementService
from src.alerts.service import AlertService
from src.projects.service import ProjectService
from src.dashboard.service import DashboardService


class TestDeviceService:

    def _db(self, app):

        return SessionLocal()



    def test_create_device(self, app):

        db = self._db(app)

        d = DeviceService(db).create('esp32-svc-1', alias='Svc Device')

        assert d.id is not None

        assert d.device_id == 'esp32-svc-1'

        assert d.alias == 'Svc Device'

        assert d.enabled is True

        assert d.api_key is not None

        db.close()



    def test_get_by_device_id(self, app):

        db = self._db(app)

        DeviceService(db).create('esp32-find')

        d = DeviceService(db).get_by_device_id('esp32-find')

        assert d is not None

        db.close()



    def test_get_by_device_id_not_found(self, app):

        db = self._db(app)

        d = DeviceService(db).get_by_device_id('nonexistent')

        assert d is None

        db.close()



    def test_get_by_api_key(self, app):

        db = self._db(app)

        device = DeviceService(db).create('esp32-key')

        found = DeviceService(db).get_by_api_key(device.api_key)

        assert found is not None

        assert found.id == device.id

        db.close()



    def test_get_by_api_key_invalid(self, app):

        db = self._db(app)

        found = DeviceService(db).get_by_api_key('invalid-key')

        assert found is None

        db.close()



    def test_get_or_create_existing(self, app):

        db = self._db(app)

        DeviceService(db).create('esp32-goc')

        d = DeviceService(db).get_or_create('esp32-goc')

        assert d.device_id == 'esp32-goc'

        db.close()



    def test_get_or_create_new(self, app):

        db = self._db(app)

        d = DeviceService(db).get_or_create('esp32-new')

        assert d.device_id == 'esp32-new'

        db.close()



    def test_touch(self, app):

        db = self._db(app)

        d = DeviceService(db).create('esp32-touch')

        assert d.last_seen is None

        DeviceService(db).touch('esp32-touch')

        assert d.last_seen is not None

        db.close()



    def test_touch_nonexistent(self, app):

        db = self._db(app)

        result = DeviceService(db).touch('nonexistent')

        assert result is None

        db.close()



    def test_regenerate_api_key(self, app):

        db = self._db(app)

        d = DeviceService(db).create('esp32-reg')

        old_key = d.api_key

        DeviceService(db).regenerate_api_key(d.id)

        assert d.api_key != old_key

        db.close()



    def test_regenerate_api_key_nonexistent(self, app):

        db = self._db(app)

        result = DeviceService(db).regenerate_api_key(99999)

        assert result is None

        db.close()



    def test_toggle_enabled(self, app):

        db = self._db(app)

        d = DeviceService(db).create('esp32-toggle')

        assert d.enabled is True

        DeviceService(db).toggle_enabled(d.id)

        assert d.enabled is False

        DeviceService(db).toggle_enabled(d.id)

        assert d.enabled is True

        db.close()



    def test_toggle_enabled_nonexistent(self, app):

        db = self._db(app)

        result = DeviceService(db).toggle_enabled(99999)

        assert result is None

        db.close()



    def test_delete(self, app):

        db = self._db(app)

        d = DeviceService(db).create('esp32-del')

        did = d.id

        assert DeviceService(db).delete(did) is True

        assert DeviceService(db).get_by_id(did) is None

        db.close()



    def test_delete_nonexistent(self, app):

        db = self._db(app)

        assert DeviceService(db).delete(99999) is False

        db.close()



    def test_get_online_status_offline_no_last_seen(self, app):

        db = self._db(app)

        d = DeviceService(db).create('esp32-stat')

        assert DeviceService.get_online_status(d) == 'offline'

        db.close()



    def test_get_online_status_online(self, app):

        db = self._db(app)

        d = DeviceService(db).create('esp32-stat-on')

        d.last_seen = datetime.now(timezone.utc)

        assert DeviceService.get_online_status(d) == 'online'

        db.close()



    def test_get_online_status_expired(self, app):

        db = self._db(app)

        d = DeviceService(db).create('esp32-stat-off')

        d.last_seen = datetime.now(timezone.utc) - timedelta(seconds=180)

        assert DeviceService.get_online_status(d) == 'offline'

        db.close()



    def test_get_online_status_naive_datetime(self, app):

        db = self._db(app)

        d = DeviceService(db).create('esp32-stat-naive')

        d.last_seen = datetime.now()

        d.last_seen = d.last_seen.replace(tzinfo=None)

        db.commit()

        status = DeviceService.get_online_status(d)

        assert status in ('online', 'offline')

        db.close()



    def test_masked_api_key_short(self, app):

        from src.devices.models import Device

        d = Device(device_id='esp32-short', api_key='abcd1234')

        assert d._masked_api_key() == 'abcd****'



    def test_update(self, app):

        db = self._db(app)

        d = DeviceService(db).create('esp32-upd')

        DeviceService(db).update(d.id, alias='Updated', description='Desc')

        assert d.alias == 'Updated'

        assert d.description == 'Desc'

        db.close()



    def test_update_nonexistent(self, app):

        db = self._db(app)

        result = DeviceService(db).update(99999, alias='Ghost')

        assert result is None

        db.close()



    def test_get_all(self, app):

        db = self._db(app)

        DeviceService(db).create('esp32-all-a')

        DeviceService(db).create('esp32-all-b')

        assert len(DeviceService(db).get_all()) >= 2

        db.close()



    def test_get_paginated(self, app):

        from sqlalchemy import insert

        from src.devices.models import Device

        db = self._db(app)

        db.execute(insert(Device), [

            {'device_id': f'esp32-page-{i}', 'api_key': DeviceService.generate_api_key()}

            for i in range(5)

        ])

        db.commit()

        p = DeviceService(db).get_paginated(page=1, per_page=2)

        assert len(p.items) == 2

        assert p.total >= 5

        db.close()





