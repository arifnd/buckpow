class TestFrontend:
    def test_dashboard_returns_html(self, client):
        resp = client.get('/')
        assert resp.status_code == 200
        assert resp.content_type.startswith('text/html')

    def test_dashboard_has_title(self, client):
        resp = client.get('/')
        assert b'BakPow' in resp.data

    def test_dashboard_has_cards(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'id="val-voltage"' in html
        assert 'id="val-current"' in html
        assert 'id="val-power"' in html
        assert 'id="val-energy"' in html

    def test_dashboard_has_chart_canvases(self, client):
        resp = client.get('/')
        assert b'id="voltageChart"' in resp.data
        assert b'id="currentChart"' in resp.data
        assert b'id="powerChart"' in resp.data
        assert b'id="energyChart"' in resp.data

    def test_dashboard_has_readings_table(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert 'id="readings-body"' in html
        for header in ['Timestamp', 'Bus V', 'Shunt V', 'Load V', 'Current', 'Power', 'Energy']:
            assert header in html

    def test_dashboard_has_static_links(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert '/static/css/style.css' in html
        assert '/static/js/charts.js' in html
        assert '/static/js/dashboard.js' in html

    def test_dashboard_has_tailwind_cdn(self, client):
        resp = client.get('/')
        assert 'cdn.tailwindcss.com' in resp.data.decode()

    def test_dashboard_has_chartjs_cdn(self, client):
        resp = client.get('/')
        assert 'cdn.jsdelivr.net/npm/chart.js' in resp.data.decode()

    def test_static_css_served(self, client):
        resp = client.get('/static/css/style.css')
        assert resp.status_code == 200

    def test_static_js_served(self, client):
        resp = client.get('/static/js/dashboard.js')
        assert resp.status_code == 200

    def test_nav_links(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        for link in ['Dashboard', 'Devices', 'Sessions', 'Measurements']:
            assert link in html


class TestPageStructure:
    def test_devices_page_has_table(self, client):
        resp = client.get('/devices')
        html = resp.data.decode()
        assert 'id="devices-body"' in html
        assert 'Add Device' in html

    def test_devices_page_has_columns(self, client):
        resp = client.get('/devices')
        html = resp.data.decode()
        for col in ['Device ID', 'Alias', 'Description', 'Status', 'Last Seen', 'Actions']:
            assert col in html

    def test_sessions_page_has_table(self, client):
        resp = client.get('/sessions')
        html = resp.data.decode()
        assert 'id="sessions-body"' in html
        assert 'Create Session' in html

    def test_sessions_page_has_columns(self, client):
        resp = client.get('/sessions')
        html = resp.data.decode()
        for col in ['Name', 'Device ID', 'Status', 'Started', 'Ended', 'Actions']:
            assert col in html

    def test_measurements_page_has_table(self, client):
        resp = client.get('/measurements')
        html = resp.data.decode()
        assert 'id="measurements-body"' in html
        assert 'Filter' in html
        assert 'Download CSV' in html

    def test_measurements_page_has_columns(self, client):
        resp = client.get('/measurements')
        html = resp.data.decode()
        for col in ['Bus V', 'Shunt V', 'Load V', 'Current', 'Power', 'Energy', 'Timestamp']:
            assert col in html

    def test_measurements_page_has_pagination(self, client):
        resp = client.get('/measurements')
        html = resp.data.decode()
        assert 'id="pagination"' in html

    def test_devices_page_has_pagination(self, client):
        resp = client.get('/devices')
        html = resp.data.decode()
        assert 'id="devices-pagination"' in html

    def test_sessions_page_has_pagination(self, client):
        resp = client.get('/sessions')
        html = resp.data.decode()
        assert 'id="sessions-pagination"' in html
