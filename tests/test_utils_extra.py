from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock


from src.utils.dates import utc_iso

from src.utils.client_ip import get_client_ip


class TestUtcIso:
    def test_none(self):
        assert utc_iso(None) is None

    def test_naive_datetime(self):
        dt = datetime(2025, 1, 15, 12, 30, 45)
        result = utc_iso(dt)
        assert result == '2025-01-15T12:30:45Z'

    def test_timezone_aware_datetime(self):
        dt = datetime(2025, 1, 15, 12, 30, 45, tzinfo=timezone.utc)
        result = utc_iso(dt)
        assert result == '2025-01-15T12:30:45Z'

    def test_non_utc_timezone(self):
        tz = timezone(timedelta(hours=7))
        dt = datetime(2025, 1, 15, 12, 30, 45, tzinfo=tz)
        result = utc_iso(dt)
        # utc_iso only replaces +00:00 with Z, non-UTC offsets stay as-is
        assert '+07:00' in result
        assert 'T12:30:45' in result


class TestGetClientIp:
    def test_x_forwarded_for(self):
        request = MagicMock()
        request.headers = {'X-Forwarded-For': '1.2.3.4, 5.6.7.8'}
        assert get_client_ip(request) == '1.2.3.4'

    def test_x_forwarded_for_single(self):
        request = MagicMock()
        request.headers = {'X-Forwarded-For': '10.0.0.1'}
        assert get_client_ip(request) == '10.0.0.1'

    def test_no_forwarded_falls_back_to_client(self):
        request = MagicMock()
        request.headers = {}
        request.client.host = '192.168.1.1'
        assert get_client_ip(request) == '192.168.1.1'

    def test_no_forwarded_no_client(self):
        request = MagicMock()
        request.headers = {}
        request.client = None
        assert get_client_ip(request) is None
