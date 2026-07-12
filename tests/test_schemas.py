import pytest
from pydantic import ValidationError

from app.schemas.measurement import MeasurementCreate
from app.schemas.session import SessionCreate, SessionUpdate
from app.schemas.device import DeviceCreate, DeviceUpdate
from app.schemas.alert import AlertCreate
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.schemas.auth import LoginRequest, ProfileUpdate
from app.schemas.settings import SettingsUpdate


class TestMeasurementCreateSchema:

    def test_valid(self):
        m = MeasurementCreate(device_id='esp32-01', bus_voltage=5.0, shunt_voltage=0.1, current=100, power=500)
        assert m.device_id == 'esp32-01'
        assert m.bus_voltage == 5.0
        assert m.firmware_version is None

    def test_with_firmware(self):
        m = MeasurementCreate(device_id='esp32-01', bus_voltage=5.0, shunt_voltage=0.1, current=100, power=500, firmware_version='1.0.0')
        assert m.firmware_version == '1.0.0'

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            MeasurementCreate(device_id='esp32-01')

    def test_wrong_type(self):
        with pytest.raises(ValidationError):
            MeasurementCreate(device_id='esp32-01', bus_voltage='not_a_number', shunt_voltage=0.1, current=100, power=500)


class TestSessionCreateSchema:

    def test_valid(self):
        s = SessionCreate(device_id=1, name='Test Session')
        assert s.device_id == 1
        assert s.name == 'Test Session'
        assert s.target_device == ''
        assert s.description == ''
        assert s.project_id is None

    def test_with_all_fields(self):
        s = SessionCreate(device_id=1, name='S', target_device='D', description='desc', project_id=5)
        assert s.target_device == 'D'
        assert s.project_id == 5

    def test_missing_name(self):
        with pytest.raises(ValidationError):
            SessionCreate(device_id=1)


class TestSessionUpdateSchema:

    def test_all_optional(self):
        s = SessionUpdate()
        assert s.name is None
        assert s.target_device is None
        assert s.description is None
        assert s.project_id is None

    def test_partial(self):
        s = SessionUpdate(name='New Name')
        assert s.name == 'New Name'
        assert s.description is None


class TestDeviceCreateSchema:

    def test_valid(self):
        d = DeviceCreate(device_id='esp32-01')
        assert d.device_id == 'esp32-01'
        assert d.alias == ''
        assert d.sampling_interval is None
        assert d.firmware_version == ''

    def test_with_all_fields(self):
        d = DeviceCreate(
            device_id='esp32-01', alias='Test', description='desc',
            sampling_interval=5, project_id=1, firmware_version='1.0',
            high_current_threshold=0.5, high_power_threshold=2.0, low_voltage_threshold=4.0,
        )
        assert d.sampling_interval == 5
        assert d.high_current_threshold == 0.5


class TestDeviceUpdateSchema:

    def test_all_optional(self):
        d = DeviceUpdate()
        assert d.alias is None
        assert d.enabled is None
        assert d.high_power_threshold is None

    def test_partial(self):
        d = DeviceUpdate(alias='New', enabled=False)
        assert d.alias == 'New'
        assert d.enabled is False


class TestAlertCreateSchema:

    def test_valid(self):
        a = AlertCreate(device_id=1, message='High power')
        assert a.device_id == 1
        assert a.level == 'warning'
        assert a.message == 'High power'

    def test_with_level(self):
        a = AlertCreate(device_id=1, level='critical', message='Overheat')
        assert a.level == 'critical'

    def test_missing_message(self):
        with pytest.raises(ValidationError):
            AlertCreate(device_id=1)


class TestProjectCreateSchema:

    def test_valid(self):
        p = ProjectCreate(name='Test Project')
        assert p.name == 'Test Project'
        assert p.description == ''

    def test_with_description(self):
        p = ProjectCreate(name='P', description='desc')
        assert p.description == 'desc'


class TestProjectUpdateSchema:

    def test_all_optional(self):
        p = ProjectUpdate()
        assert p.name is None
        assert p.description is None


class TestLoginRequestSchema:

    def test_valid(self):
        l = LoginRequest(email='user@test.com', password='pass')
        assert l.email == 'user@test.com'
        assert l.password == 'pass'

    def test_missing_fields(self):
        with pytest.raises(ValidationError):
            LoginRequest(email='user@test.com')


class TestProfileUpdateSchema:

    def test_all_optional(self):
        p = ProfileUpdate()
        assert p.name is None
        assert p.email is None
        assert p.password is None

    def test_partial(self):
        p = ProfileUpdate(name='New')
        assert p.name == 'New'
        assert p.email is None


class TestSettingsUpdateSchema:

    def test_all_optional(self):
        s = SettingsUpdate()
        assert s.high_power_threshold is None
        assert s.brand is None
        assert s.timezone is None

    def test_union_types(self):
        s = SettingsUpdate(high_power_threshold=2.5)
        assert s.high_power_threshold == 2.5
        s2 = SettingsUpdate(high_power_threshold='3.0')
        assert s2.high_power_threshold == '3.0'
