from pydantic import ValidationError


from src.devices.schemas import DeviceCreate, DeviceUpdate

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


