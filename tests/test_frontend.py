class TestFrontend:
    def test_dashboard_returns_html(self, client):
        resp = client.get('/')
        assert resp.status_code == 200
        assert resp.content_type.startswith('text/html')

    def test_dashboard_has_title(self, client):
        resp = client.get('/')
        assert b'PowerDash' in resp.data

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
        for header in ['Timestamp', 'Bus Voltage', 'Shunt Voltage', 'Load Voltage', 'Current', 'Power', 'Energy']:
            assert header in html

    def test_dashboard_has_static_links(self, client):
        resp = client.get('/')
        html = resp.data.decode()
        assert '/static/css/style.css' in html
        assert '/static/js/charts.js' in html
        assert '/static/js/dashboard.js' in html

    def test_dashboard_has_chartjs_cdn(self, client):
        resp = client.get('/')
        assert 'cdn.jsdelivr.net/npm/chart.js' in resp.data.decode()

    def test_dashboard_has_bootstrap_cdn(self, client):
        resp = client.get('/')
        assert 'cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css' in resp.data.decode()

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
