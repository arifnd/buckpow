from pydantic import ValidationError


from src.settings.schemas import SettingsUpdate

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
