import re


HREF_RE = re.compile(r'href="([^"]+)"')
SCRIPT_RE = re.compile(r'<script[^>]*>.*?</script>', re.DOTALL)


def extract_links(html):
    clean = SCRIPT_RE.sub('', html)
    links = set()
    for match in HREF_RE.finditer(clean):
        href = match.group(1)
        if href.startswith(('http://', 'https://', 'mailto:', 'tel:', 'javascript:', '#')):
            continue
        href = href.split('?')[0].split('#')[0]
        if href:
            links.add(href)
    return links


class TestDeadLinks:
    def test_dashboard_has_no_broken_links(self, client):
        resp = client.get('/')
        links = extract_links(resp.content.decode())
        broken = []
        for link in links:
            r = client.get(link, follow_redirects=False)
            if r.status_code not in (200, 302):
                broken.append((link, r.status_code))
        assert not broken, f'Dashboard has broken links: {broken}'

    def test_devices_has_no_broken_links(self, client):
        resp = client.get('/devices')
        links = extract_links(resp.content.decode())
        broken = []
        for link in links:
            r = client.get(link, follow_redirects=False)
            if r.status_code not in (200, 302):
                broken.append((link, r.status_code))
        assert not broken, f'Devices has broken links: {broken}'

    def test_devices_new_has_no_broken_links(self, client):
        resp = client.get('/devices/new')
        links = extract_links(resp.content.decode())
        broken = []
        for link in links:
            r = client.get(link, follow_redirects=False)
            if r.status_code not in (200, 302):
                broken.append((link, r.status_code))
        assert not broken, f'Devices new has broken links: {broken}'

    def test_sessions_has_no_broken_links(self, client):
        resp = client.get('/sessions')
        links = extract_links(resp.content.decode())
        broken = []
        for link in links:
            r = client.get(link, follow_redirects=False)
            if r.status_code not in (200, 302):
                broken.append((link, r.status_code))
        assert not broken, f'Sessions has broken links: {broken}'

    def test_sessions_new_has_no_broken_links(self, client):
        resp = client.get('/sessions/new')
        links = extract_links(resp.content.decode())
        broken = []
        for link in links:
            r = client.get(link, follow_redirects=False)
            if r.status_code not in (200, 302):
                broken.append((link, r.status_code))
        assert not broken, f'Sessions new has broken links: {broken}'

    def test_session_detail_has_no_broken_links(self, client):
        from src.database import SessionLocal
        from src.devices.models import Device
        from src.sessions.models import Session
        db = SessionLocal()
        d = Device(device_id='esp32-link-detail', alias='Link Detail Device', sampling_interval=1)
        db.add(d)
        db.commit()
        s = Session(name='Link Detail Session', device_id=d.id, status='draft')
        db.add(s)
        db.commit()
        sid = s.id
        db.close()
        resp = client.get(f'/sessions/{sid}')
        links = extract_links(resp.content.decode())
        broken = []
        for link in links:
            r = client.get(link, follow_redirects=False)
            if r.status_code not in (200, 302):
                broken.append((link, r.status_code))
        assert not broken, f'Session detail has broken links: {broken}'

    def test_projects_has_no_broken_links(self, client):
        resp = client.get('/projects')
        links = extract_links(resp.content.decode())
        broken = []
        for link in links:
            r = client.get(link, follow_redirects=False)
            if r.status_code not in (200, 302):
                broken.append((link, r.status_code))
        assert not broken, f'Projects has broken links: {broken}'

    def test_measurements_has_no_broken_links(self, client):
        resp = client.get('/measurements')
        links = extract_links(resp.content.decode())
        broken = []
        for link in links:
            r = client.get(link, follow_redirects=False)
            if r.status_code not in (200, 302):
                broken.append((link, r.status_code))
        assert not broken, f'Measurements has broken links: {broken}'

    def test_benchmark_has_no_broken_links(self, client):
        resp = client.get('/benchmark')
        links = extract_links(resp.content.decode())
        broken = []
        for link in links:
            r = client.get(link, follow_redirects=False)
            if r.status_code not in (200, 302):
                broken.append((link, r.status_code))
        assert not broken, f'Benchmark has broken links: {broken}'

    def test_alerts_has_no_broken_links(self, client):
        resp = client.get('/alerts')
        links = extract_links(resp.content.decode())
        broken = []
        for link in links:
            r = client.get(link, follow_redirects=False)
            if r.status_code not in (200, 302):
                broken.append((link, r.status_code))
        assert not broken, f'Alerts has broken links: {broken}'

    def test_settings_has_no_broken_links(self, client):
        resp = client.get('/settings')
        links = extract_links(resp.content.decode())
        broken = []
        for link in links:
            r = client.get(link, follow_redirects=False)
            if r.status_code not in (200, 302):
                broken.append((link, r.status_code))
        assert not broken, f'Settings has broken links: {broken}'

    def test_profile_has_no_broken_links(self, client):
        resp = client.get('/profile')
        links = extract_links(resp.content.decode())
        broken = []
        for link in links:
            r = client.get(link, follow_redirects=False)
            if r.status_code not in (200, 302):
                broken.append((link, r.status_code))
        assert not broken, f'Profile has broken links: {broken}'

    def test_audit_has_no_broken_links(self, client):
        resp = client.get('/audit')
        links = extract_links(resp.content.decode())
        broken = []
        for link in links:
            r = client.get(link, follow_redirects=False)
            if r.status_code not in (200, 302):
                broken.append((link, r.status_code))
        assert not broken, f'Audit has broken links: {broken}'

    def test_sidebar_links_are_valid(self, client):
        resp = client.get('/')
        html = resp.content.decode()
        for link in ['/', '/devices', '/sessions', '/projects', '/measurements', '/benchmark', '/alerts', '/audit']:
            assert f'href="{link}"' in html
            r = client.get(link)
            assert r.status_code == 200

    def test_header_links_are_valid(self, client):
        resp = client.get('/')
        html = resp.content.decode()
        for link in ['/profile', '/settings']:
            assert f'href="{link}"' in html
            r = client.get(link)
            assert r.status_code == 200

    def test_login_page_links_are_valid(self, unauth_client):
        resp = unauth_client.get('/auth/login')
        links = extract_links(resp.content.decode())
        for link in links:
            r = unauth_client.get(link, follow_redirects=False)
            assert r.status_code in (200, 302)

    def test_static_asset_links_are_reachable(self, client):
        resp = client.get('/')
        static_links = re.findall(r'(?:href|src)="(/static/[^"]+)"', resp.content.decode())
        for link in static_links:
            r = client.get(link)
            assert r.status_code == 200
