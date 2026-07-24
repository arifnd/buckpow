import pytest
from pydantic import ValidationError
from src.alerts.schemas import AlertCreate


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


