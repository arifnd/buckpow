import pytest
from pydantic import ValidationError


from src.measurements.schemas import MeasurementCreate

class TestMeasurementCreateSchema:

    def test_valid(self):
        m = MeasurementCreate(device_id='esp32-01', bus_voltage=5.0, shunt_voltage=0.1, current=100, power=500)
        assert m.device_id == 'esp32-01'
        assert m.bus_voltage == 5.0
        assert m.firmware_version is None

    def test_with_firmware(self):
        m = MeasurementCreate(device_id='esp32-01', bus_voltage=5.0, shunt_voltage=0.1, current=100, power=500, firmware_version='1.0.0')
        assert m.firmware_version == '1.0.0'

    def test_pzem_no_shunt_voltage(self):
        m = MeasurementCreate(device_id='pzem-01', bus_voltage=230.5, current=4500, power=1035000)
        assert m.shunt_voltage == 0.0
        assert m.bus_voltage == 230.5

    def test_pzem_ac_voltage_values(self):
        m = MeasurementCreate(device_id='pzem-01', bus_voltage=220.0, current=10000, power=2200000)
        assert m.bus_voltage == 220.0
        assert m.current == 10000

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            MeasurementCreate(device_id='esp32-01')

    def test_wrong_type(self):
        with pytest.raises(ValidationError):
            MeasurementCreate(device_id='esp32-01', bus_voltage='not_a_number', shunt_voltage=0.1, current=100, power=500)


