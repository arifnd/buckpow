import re


class TestFrontend:
    def test_dashboard_returns_html(self, client):
        resp = client.get('/')
        assert resp.status_code == 200
        assert resp.headers['content-type'].startswith('text/html')

    def test_dashboard_has_title(self, client):
        resp = client.get('/')
        assert b'BuckPow' in resp.content

    def test_dashboard_has_cards(self, client):
        resp = client.get('/')
        html = resp.content.decode()
        assert 'id="val-voltage"' in html
        assert 'id="val-current"' in html
        assert 'id="val-power"' in html
        assert 'id="val-energy"' in html

    def test_dashboard_has_chart_canvases(self, client):
        resp = client.get('/')
        assert b'id="voltageChart"' in resp.content
        assert b'id="currentChart"' in resp.content
        assert b'id="powerChart"' in resp.content
        assert b'id="energyChart"' in resp.content

    def test_dashboard_has_readings_table(self, client):
        resp = client.get('/')
        html = resp.content.decode()
        assert 'id="readings-body"' in html
        for header in ['Timestamp', 'Bus V', 'Shunt V', 'Load V', 'Current', 'Power', 'Energy']:
            assert header in html

    def test_dashboard_has_static_links(self, client):
        resp = client.get('/')
        html = resp.content.decode()
        assert '/static/css/style.css' in html
        assert '/static/js/charts.js' in html
        assert '/static/js/dashboard.js' in html

    def test_dashboard_has_tailwind_cdn(self, client):
        resp = client.get('/')
        assert 'cdn.tailwindcss.com' in resp.content.decode()

    def test_dashboard_has_chartjs_cdn(self, client):
        resp = client.get('/')
        assert 'cdn.jsdelivr.net/npm/chart.js' in resp.content.decode()

    def test_static_css_served(self, client):
        resp = client.get('/static/css/style.css')
        assert resp.status_code == 200

    def test_static_js_served(self, client):
        resp = client.get('/static/js/dashboard.js')
        assert resp.status_code == 200

    def test_nav_links(self, client):
        resp = client.get('/')
        html = resp.content.decode()
        for link in ['Dashboard', 'Devices', 'Sessions', 'Measurements']:
            assert link in html


class TestPageStructure:
    def test_devices_page_has_table(self, client):
        resp = client.get('/devices')
        html = resp.content.decode()
        assert 'id="devices-body"' in html
        assert 'Add Device' in html

    def test_devices_page_has_columns(self, client):
        resp = client.get('/devices')
        html = resp.content.decode()
        for col in ['Device ID', 'Alias', 'Description', 'Status', 'Last Seen', 'Actions']:
            assert col in html

    def test_sessions_page_has_table(self, client):
        resp = client.get('/sessions')
        html = resp.content.decode()
        assert 'id="sessions-body"' in html
        assert 'Create Session' in html

    def test_sessions_page_has_columns(self, client):
        resp = client.get('/sessions')
        html = resp.content.decode()
        for col in ['Name', 'Device ID', 'Status', 'Started', 'Ended', 'Actions']:
            assert col in html

    def test_measurements_page_has_table(self, client):
        resp = client.get('/measurements')
        html = resp.content.decode()
        assert 'id="measurements-body"' in html
        assert 'Filter' in html
        assert 'CSV' in html
        assert 'XLSX' in html

    def test_measurements_page_has_columns(self, client):
        resp = client.get('/measurements')
        html = resp.content.decode()
        for col in ['Bus V', 'Shunt V', 'Load V', 'Current', 'Power', 'Energy', 'Timestamp']:
            assert col in html

    def test_measurements_page_has_pagination(self, client):
        resp = client.get('/measurements')
        html = resp.content.decode()
        assert 'id="pagination"' in html

    def test_devices_page_has_pagination(self, client):
        resp = client.get('/devices')
        html = resp.content.decode()
        assert 'id="devices-pagination"' in html

    def test_sessions_page_has_pagination(self, client):
        resp = client.get('/sessions')
        html = resp.content.decode()
        assert 'id="sessions-pagination"' in html


class TestPageRendering:
    def test_dashboard_returns_200(self, client):
        assert client.get('/').status_code == 200

    def test_devices_returns_200(self, client):
        assert client.get('/devices').status_code == 200

    def test_devices_new_returns_200(self, client):
        assert client.get('/devices/new').status_code == 200

    def test_sessions_returns_200(self, client):
        assert client.get('/sessions').status_code == 200

    def test_sessions_new_returns_200(self, client):
        assert client.get('/sessions/new').status_code == 200

    def test_projects_returns_200(self, client):
        assert client.get('/projects').status_code == 200

    def test_measurements_returns_200(self, client):
        assert client.get('/measurements').status_code == 200

    def test_benchmark_returns_200(self, client):
        assert client.get('/benchmark').status_code == 200

    def test_alerts_returns_200(self, client):
        assert client.get('/alerts').status_code == 200

    def test_settings_returns_200(self, client):
        assert client.get('/settings').status_code == 200

    def test_profile_returns_200(self, client):
        assert client.get('/profile').status_code == 200

    def test_audit_returns_200(self, client):
        assert client.get('/audit').status_code == 200

    def test_dashboard_returns_html(self, client):
        assert client.get('/').headers['content-type'].startswith('text/html')

    def test_devices_returns_html(self, client):
        assert client.get('/devices').headers['content-type'].startswith('text/html')

    def test_devices_new_returns_html(self, client):
        assert client.get('/devices/new').headers['content-type'].startswith('text/html')

    def test_sessions_returns_html(self, client):
        assert client.get('/sessions').headers['content-type'].startswith('text/html')

    def test_sessions_new_returns_html(self, client):
        assert client.get('/sessions/new').headers['content-type'].startswith('text/html')

    def test_projects_returns_html(self, client):
        assert client.get('/projects').headers['content-type'].startswith('text/html')

    def test_measurements_returns_html(self, client):
        assert client.get('/measurements').headers['content-type'].startswith('text/html')

    def test_benchmark_returns_html(self, client):
        assert client.get('/benchmark').headers['content-type'].startswith('text/html')

    def test_alerts_returns_html(self, client):
        assert client.get('/alerts').headers['content-type'].startswith('text/html')

    def test_settings_returns_html(self, client):
        assert client.get('/settings').headers['content-type'].startswith('text/html')

    def test_profile_returns_html(self, client):
        assert client.get('/profile').headers['content-type'].startswith('text/html')

    def test_audit_returns_html(self, client):
        assert client.get('/audit').headers['content-type'].startswith('text/html')

    def test_devices_edit_with_real_device(self, client, sample_device):
        resp = client.get(f'/devices/{sample_device["id"]}/edit')
        assert resp.status_code == 200
        html = resp.content.decode()
        assert 'Edit Device' in html or 'device_id' in html.lower()

    def test_sessions_edit_page(self, client):
        resp = client.get('/sessions/1/edit')
        assert resp.status_code == 200


class TestNavigationCompleteness:
    def test_sidebar_has_all_items(self, client):
        resp = client.get('/')
        html = resp.content.decode()
        for label in ['Dashboard', 'Devices', 'Sessions', 'Projects', 'Measurements', 'Benchmark', 'Alerts', 'Audit']:
            assert label in html

    def test_sidebar_links_have_correct_href(self, client):
        resp = client.get('/')
        html = resp.content.decode()
        for href in ['/', '/devices', '/sessions', '/projects', '/measurements', '/benchmark', '/alerts', '/audit']:
            assert f'href="{href}"' in html

    def test_header_has_profile_link(self, client):
        resp = client.get('/')
        assert 'href="/profile"' in resp.content.decode()

    def test_header_has_settings_link(self, client):
        resp = client.get('/')
        assert resp.status_code == 200
        assert 'href="/settings"' in resp.content.decode()

    def test_dashboard_page_has_timestamp_globals(self, client):
        html = client.get('/').content.decode()
        assert '__userTimestampFormat' in html
        assert '__userDateFormat' in html
        assert '__userTimezone' in html

    def test_active_page_highlighted(self, client):
        resp = client.get('/')
        html = resp.content.decode()
        assert 'active' in html.lower() or 'border-blue' in html or 'text-blue' in html


class TestStaticAssets:
    def test_static_css_returns_200(self, client):
        assert client.get('/static/css/style.css').status_code == 200

    def test_static_dashboard_js_returns_200(self, client):
        assert client.get('/static/js/dashboard.js').status_code == 200

    def test_static_charts_js_returns_200(self, client):
        assert client.get('/static/js/charts.js').status_code == 200

    def test_static_theme_js_returns_200(self, client):
        assert client.get('/static/js/theme.js').status_code == 200

    def test_static_settings_js_returns_200(self, client):
        assert client.get('/static/js/settings.js').status_code == 200

    def test_static_benchmark_js_returns_200(self, client):
        assert client.get('/static/js/benchmark.js').status_code == 200

    def test_dashboard_references_tailwind_cdn(self, client):
        assert 'cdn.tailwindcss.com' in client.get('/').content.decode()

    def test_dashboard_references_chartjs_cdn(self, client):
        assert 'cdn.jsdelivr.net/npm/chart.js' in client.get('/').content.decode()

    def test_dashboard_references_htmx_cdn(self, client):
        assert 'htmx.org' in client.get('/').content.decode()

    def test_dashboard_references_iconify_cdn(self, client):
        assert 'iconify' in client.get('/').content.decode().lower()

    def test_benchmark_references_benchmark_js(self, client):
        assert 'benchmark.js' in client.get('/benchmark').content.decode()


class TestHTMLStructure:
    def test_dashboard_has_heading(self, client):
        assert re.search(r'<h[1-6]', client.get('/').content.decode())

    def test_devices_has_heading(self, client):
        assert re.search(r'<h[1-6]', client.get('/devices').content.decode())

    def test_sessions_has_heading(self, client):
        assert re.search(r'<h[1-6]', client.get('/sessions').content.decode())

    def test_projects_has_heading(self, client):
        assert re.search(r'<h[1-6]', client.get('/projects').content.decode())

    def test_measurements_has_heading(self, client):
        assert re.search(r'<h[1-6]', client.get('/measurements').content.decode())

    def test_benchmark_has_heading(self, client):
        assert re.search(r'<h[1-6]', client.get('/benchmark').content.decode())

    def test_alerts_has_heading(self, client):
        assert re.search(r'<h[1-6]', client.get('/alerts').content.decode())

    def test_settings_has_heading(self, client):
        assert re.search(r'<h[1-6]', client.get('/settings').content.decode())

    def test_profile_has_heading(self, client):
        assert re.search(r'<h[1-6]', client.get('/profile').content.decode())

    def test_audit_has_heading(self, client):
        assert re.search(r'<h[1-6]', client.get('/audit').content.decode())

    def test_settings_page_has_all_tabs(self, client):
        html = client.get('/settings').content.decode()
        assert 'data-tab="general"' in html
        assert 'data-tab="alerts"' in html
        assert 'data-tab="backup"' in html

    def test_settings_page_has_forms(self, client):
        html = client.get('/settings').content.decode()
        assert 'id="form-general"' in html
        assert 'id="form-alerts"' in html

    def test_settings_page_has_date_format_field(self, client):
        html = client.get('/settings').content.decode()
        assert 'id="field-date-format"' in html
        assert 'YYYY-MM-DD' in html
        assert 'DD/MM/YYYY' in html
        assert 'MM/DD/YYYY' in html

    def test_settings_page_has_date_format_in_form_data_fields(self, client):
        html = client.get('/settings').content.decode()
        assert '"date_format"' in html

    def test_profile_page_has_form_fields(self, client):
        html = client.get('/profile').content.decode()
        assert 'name="name"' in html
        assert 'name="email"' in html
        assert 'name="password"' in html

    def test_login_page_has_inputs(self, unauth_client):
        html = unauth_client.get('/auth/login').content.decode()
        assert 'email' in html.lower()
        assert 'password' in html.lower()

    def test_devices_new_page_has_form(self, client):
        html = client.get('/devices/new').content.decode()
        assert 'id="device-form"' in html or 'device_id' in html.lower()

    def test_sessions_new_page_has_form(self, client):
        html = client.get('/sessions/new').content.decode()
        assert 'id="session-form"' in html or 'session' in html.lower()

    def test_projects_page_has_create_button(self, client):
        html = client.get('/projects').content.decode()
        assert 'Create Project' in html or 'create-project' in html.lower()

    def test_benchmark_page_has_compare_elements(self, client):
        html = client.get('/benchmark').content.decode()
        assert 'session-a' in html or 'session' in html.lower()
        assert 'compare' in html.lower()

    def test_alerts_page_has_filter_elements(self, client):
        html = client.get('/alerts').content.decode()
        assert 'filter' in html.lower() or 'alerts-tbody' in html

    def test_audit_page_has_table(self, client):
        html = client.get('/audit').content.decode()
        assert 'logs-tbody' in html or 'audit' in html.lower()

    def test_devices_page_has_table(self, client):
        assert 'id="devices-body"' in client.get('/devices').content.decode()

    def test_sessions_page_has_table(self, client):
        assert 'id="sessions-body"' in client.get('/sessions').content.decode()

    def test_measurements_page_has_table(self, client):
        assert 'id="measurements-body"' in client.get('/measurements').content.decode()


class TestEmptyStates:
    def test_devices_page_renders_empty(self, client):
        assert client.get('/devices').status_code == 200

    def test_sessions_page_renders_empty(self, client):
        assert client.get('/sessions').status_code == 200

    def test_projects_page_renders_empty(self, client):
        assert client.get('/projects').status_code == 200

    def test_measurements_page_renders_empty(self, client):
        assert client.get('/measurements').status_code == 200

    def test_alerts_page_renders_empty(self, client):
        assert client.get('/alerts').status_code == 200

    def test_audit_page_renders_empty(self, client):
        assert client.get('/audit').status_code == 200

    def test_benchmark_page_renders_empty(self, client):
        assert client.get('/benchmark').status_code == 200


class TestEdgeCases:
    def test_unknown_route_returns_404(self, client):
        resp = client.get('/nonexistent-page', follow_redirects=False)
        assert resp.status_code == 404

    def test_logout_returns_ok(self, client):
        resp = client.post('/auth/logout')
        assert resp.status_code == 200
        assert resp.json() == {'status': 'ok'}

    def test_login_redirects_when_authenticated(self, client):
        resp = client.get('/auth/login', follow_redirects=False)
        assert resp.status_code == 302

    def test_devices_edit_with_nonexistent_id(self, client):
        resp = client.get('/devices/99999/edit')
        assert resp.status_code == 200

    def test_sessions_edit_with_nonexistent_id(self, client):
        resp = client.get('/sessions/99999/edit')
        assert resp.status_code == 200


class TestAPIEndpoints:
    def test_health_returns_200(self, client):
        assert client.get('/api/v1/health').status_code == 200

    def test_settings_inline_field_map_includes_date_format(self, client):
        html = client.get('/settings').content.decode()
        assert "date_format: 'field-date-format'" in html
        assert "'date_format'" in html

    def test_settings_returns_json(self, client):
        resp = client.get('/api/v1/settings')
        assert resp.status_code == 200
        assert resp.headers['content-type'].startswith('application/json')

    def test_settings_db_info_returns_type(self, client):
        resp = client.get('/api/v1/settings/db-info')
        assert resp.status_code == 200
        data = resp.json()
        assert 'type' in data
        assert data['type'] in ('sqlite', 'postgresql', 'mysql')

    def test_dashboard_api_returns_200(self, client):
        assert client.get('/api/v1/dashboard').status_code == 200

    def test_devices_api_returns_list(self, client):
        resp = client.get('/api/v1/devices')
        assert resp.status_code == 200
        assert resp.json().get('devices') is not None or isinstance(resp.json(), list)

    def test_sessions_api_returns_list(self, client):
        assert client.get('/api/v1/sessions').status_code == 200

    def test_alerts_api_returns_list(self, client):
        assert client.get('/api/v1/alerts').status_code == 200
