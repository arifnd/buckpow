from src import app
from src.config import settings


class TestAPIDocsEnabled:
    def test_docs_returns_200(self, client):
        resp = client.get("/docs")
        assert resp.status_code == 200

    def test_redoc_returns_200(self, client):
        resp = client.get("/redoc")
        assert resp.status_code == 200

    def test_openapi_json_returns_200(self, client):
        resp = client.get("/openapi.json")
        assert resp.status_code == 200

    def test_config_disabled_default(self):
        assert settings.DISABLE_API_DOCS is False

    def test_app_has_docs_url(self):
        assert app.docs_url == "/docs"
        assert app.redoc_url == "/redoc"
        assert app.openapi_url == "/openapi.json"
