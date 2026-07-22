import json
import time
from collections import defaultdict


def bearer_token_key(scope):
    for name, value in scope.get("headers", []):
        if name == b"authorization":
            auth = value.decode()
            if auth.startswith("Bearer "):
                return auth[7:]
    return None


class RateLimiterMiddleware:
    def __init__(self, app, limits=None):
        self.app = app
        self.limits = limits or []
        self.requests = defaultdict(list)
        self._cleanup_counter = 0

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        client_ip = scope.get("client", ("127.0.0.1", 0))[0]
        method = scope["method"]
        path = scope["path"]

        max_reqs = window = key_func = None
        for entry in self.limits:
            meth, prefix, mr, w = entry[:4]
            if path.startswith(prefix) and (meth is None or meth == method):
                max_reqs, window = mr, w
                key_func = entry[4] if len(entry) > 4 else None
                break

        if max_reqs is None:
            await self.app(scope, receive, send)
            return

        identity = key_func(scope) if key_func else None
        if identity is None:
            identity = client_ip

        now = time.time()
        key = f"{identity}:{method}:{prefix}"
        timestamps = self.requests[key]
        cutoff = now - window
        self.requests[key] = [t for t in timestamps if t > cutoff]

        if len(self.requests[key]) >= max_reqs:
            body = json.dumps(
                {"error": "Rate limit exceeded", "code": "RATE_LIMITED"}
            ).encode()
            headers = [
                (b"content-type", b"application/json"),
                (b"retry-after", str(int(window)).encode()),
            ]
            await send(
                {
                    "type": "http.response.start",
                    "status": 429,
                    "headers": headers,
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": body,
                }
            )
            return

        self.requests[key].append(now)

        self._cleanup_counter += 1
        if self._cleanup_counter > 100:
            self._cleanup_counter = 0
            self._trim()

        await self.app(scope, receive, send)

    def _trim(self):
        now = time.time()
        keys = list(self.requests.keys())
        for k in keys:
            self.requests[k] = [t for t in self.requests[k] if t > now - 120]
            if not self.requests[k]:
                del self.requests[k]
