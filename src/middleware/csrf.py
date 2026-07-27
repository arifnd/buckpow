import hashlib
import hmac
import secrets
import time


class CSRFMiddleware:
    """Double-submit cookie CSRF protection for HTMX dashboard.

    Only enforces for HTMX requests (requests with HX-Request header).
    Exempts:
    - GET/HEAD/OPTIONS requests (safe methods)
    - API endpoints with Bearer token auth (/api/v1/measurements, etc.)
    - Static files
    - Non-HTMX requests (protected by SameSite cookies)
    """

    EXEMPT_PREFIXES = ("/api/", "/static/")
    EXEMPT_METHODS = {"GET", "HEAD", "OPTIONS"}

    def __init__(self, app, secret_key: str, max_age: int = 3600):
        self.app = app
        self.secret_key = secret_key.encode()
        self.max_age = max_age

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        method = scope["method"].upper()
        path = scope["path"]

        # Skip safe methods
        if method in self.EXEMPT_METHODS:
            return await self.app(scope, receive, send)

        # Skip API endpoints (they use Bearer token auth)
        if any(path.startswith(p) for p in self.EXEMPT_PREFIXES):
            return await self.app(scope, receive, send)

        # Only enforce CSRF for HTMX requests
        headers = dict(scope.get("headers", []))
        is_htmx = b"hx-request" in headers

        if not is_htmx:
            return await self.app(scope, receive, send)

        # Validate CSRF token from header
        token = headers.get(b"x-csrf-token", b"").decode()

        if not self._validate_token(token):
            from fastapi.responses import JSONResponse

            response = JSONResponse(
                status_code=403,
                content={"error": "CSRF validation failed", "code": "CSRF_ERROR"},
            )
            return await response(scope, receive, send)

        return await self.app(scope, receive, send)

    def _validate_token(self, token: str) -> bool:
        if not token:
            return False
        try:
            parts = token.split(":")
            if len(parts) != 3:
                return False
            timestamp_str, nonce, signature = parts
            timestamp = int(timestamp_str)

            # Check expiry
            if time.time() - timestamp > self.max_age:
                return False

            # Verify signature
            expected = self._sign(timestamp_str, nonce)
            return hmac.compare_digest(signature, expected)
        except (ValueError, IndexError):
            return False

    def _sign(self, timestamp: str, nonce: str) -> str:
        message = f"{timestamp}:{nonce}"
        return hmac.new(self.secret_key, message.encode(), hashlib.sha256).hexdigest()[:32]

    def generate_token(self) -> str:
        timestamp = str(int(time.time()))
        nonce = secrets.token_hex(16)
        signature = self._sign(timestamp, nonce)
        return f"{timestamp}:{nonce}:{signature}"
