from src.middleware.rate_limiter import RateLimiterMiddleware, bearer_token_key


class TestBearerTokenKey:

    def test_extracts_bearer_token(self):
        scope = {'headers': [(b'authorization', b'Bearer my-api-key-123')]}
        assert bearer_token_key(scope) == 'my-api-key-123'

    def test_no_auth_header(self):
        assert bearer_token_key({'headers': []}) is None

    def test_not_bearer(self):
        scope = {'headers': [(b'authorization', b'Basic xyz')]}
        assert bearer_token_key(scope) is None

    def test_no_headers_key(self):
        assert bearer_token_key({}) is None


def _make_scope(method='POST', path='/api/v1/measurements', ip='1.2.3.4', token=None):
    headers = []
    if token:
        headers.append((b'authorization', f'Bearer {token}'.encode()))
    return {
        'type': 'http',
        'method': method,
        'path': path,
        'client': (ip, 0),
        'headers': headers,
    }


class TestRateLimiterMiddleware:

    def test_no_match_passes_through(self):
        tracker = {'calls': 0}

        async def dummy_app(scope, receive, send):
            tracker['calls'] += 1

        async def send(msg):
            pass

        mw = RateLimiterMiddleware(dummy_app, limits=[('POST', '/api/v1/measurements', 1, 60)])
        scope = _make_scope(method='GET', path='/api/v1/health')

        import asyncio
        asyncio.run(mw(scope, None, send))

        assert tracker['calls'] == 1

    def test_limit_not_reached(self):
        tracker = {'calls': 0}

        async def dummy_app(scope, receive, send):
            tracker['calls'] += 1

        async def send(msg):
            pass

        mw = RateLimiterMiddleware(dummy_app, limits=[('POST', '/api/v1/measurements', 60, 60, bearer_token_key)])
        scope = _make_scope(token='device-key-1')

        import asyncio
        asyncio.run(mw(scope, None, send))

        assert tracker['calls'] == 1

    def test_limit_exceeded(self):
        tracker = {'calls': 0, 'sent': []}

        async def dummy_app(scope, receive, send):
            tracker['calls'] += 1

        async def send(msg):
            tracker['sent'].append(msg)

        mw = RateLimiterMiddleware(dummy_app, limits=[('POST', '/api/v1/measurements', 2, 60, bearer_token_key)])
        scope = _make_scope(token='device-key-1')

        import asyncio
        asyncio.run(mw(scope, None, send))
        asyncio.run(mw(scope, None, send))
        asyncio.run(mw(scope, None, send))

        assert tracker['calls'] == 2
        assert len(tracker['sent']) == 2  # start + body per rate-limited request
        assert tracker['sent'][0]['type'] == 'http.response.start'
        assert tracker['sent'][0]['status'] == 429

    def test_different_keys_separate_counters(self):
        tracker = {'calls': 0, 'sent': []}

        async def dummy_app(scope, receive, send):
            tracker['calls'] += 1

        async def send(msg):
            tracker['sent'].append(msg)

        mw = RateLimiterMiddleware(dummy_app, limits=[('POST', '/api/v1/measurements', 2, 60, bearer_token_key)])
        scope1 = _make_scope(token='device-key-1')
        scope2 = _make_scope(token='device-key-2')

        import asyncio
        for _ in range(3):
            asyncio.run(mw(scope1, None, send))
        for _ in range(3):
            asyncio.run(mw(scope2, None, send))

        assert tracker['calls'] == 4
        assert len(tracker['sent']) == 4  # 2 rate-limited requests × 2 messages each

    def test_no_bearer_falls_back_to_ip(self):
        tracker = {'calls': 0, 'sent': []}

        async def dummy_app(scope, receive, send):
            tracker['calls'] += 1

        async def send(msg):
            tracker['sent'].append(msg)

        mw = RateLimiterMiddleware(dummy_app, limits=[('POST', '/api/v1/measurements', 2, 60, bearer_token_key)])
        scope = _make_scope(ip='5.6.7.8', token=None)

        import asyncio
        for _ in range(3):
            asyncio.run(mw(scope, None, send))

        assert tracker['calls'] == 2
        assert len(tracker['sent']) == 2

    def test_login_ip_based_limiting(self):
        tracker = {'calls': 0, 'sent': []}

        async def dummy_app(scope, receive, send):
            tracker['calls'] += 1

        async def send(msg):
            tracker['sent'].append(msg)

        mw = RateLimiterMiddleware(dummy_app, limits=[('POST', '/api/v1/auth/login', 5, 60)])
        scope = _make_scope(method='POST', path='/api/v1/auth/login', ip='9.9.9.9')

        import asyncio
        for _ in range(7):
            asyncio.run(mw(scope, None, send))

        assert tracker['calls'] == 5
        assert len(tracker['sent']) == 4  # 2 rate-limited requests × 2 messages each

    def test_non_http_scope_passthrough(self):
        tracker = {'calls': 0}

        async def dummy_app(scope, receive, send):
            tracker['calls'] += 1

        async def send(msg):
            pass

        mw = RateLimiterMiddleware(dummy_app, limits=[('POST', '/api/v1/measurements', 1, 60)])
        scope = {'type': 'websocket'}

        import asyncio
        asyncio.run(mw(scope, None, send))
        assert tracker['calls'] == 1

    def test_trim_cleans_old_entries(self):
        import time
        mw = RateLimiterMiddleware(lambda s, r, s2: None, limits=[])
        key = 'test-key'
        now = time.time()
        mw.requests[key] = [now - 200, now - 50, now]
        mw._trim()
        assert len(mw.requests[key]) == 2  # -200 is trimmed, -50 and now remain

    def test_trim_removes_empty_keys(self):
        import time
        mw = RateLimiterMiddleware(lambda s, r, s2: None, limits=[])
        key = 'old-key'
        mw.requests[key] = [time.time() - 200]
        mw._trim()
        assert key not in mw.requests

    def test_cleanup_counter_triggers_trim(self):
        tracker = {'calls': 0}

        async def dummy_app(scope, receive, send):
            tracker['calls'] += 1

        async def send(msg):
            pass

        mw = RateLimiterMiddleware(dummy_app, limits=[('POST', '/api/v1/measurements', 1000, 60)])
        mw._cleanup_counter = 100

        scope = _make_scope()
        import asyncio
        asyncio.run(mw(scope, None, send))
        assert mw._cleanup_counter == 0
        assert tracker['calls'] == 1
