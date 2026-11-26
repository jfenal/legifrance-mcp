import pytest

from server import _build_http_app, _select_transport
from server import server


class TestSelectTransport:
    def test_defaults_to_stdio_when_unset(self, monkeypatch):
        monkeypatch.delenv("MCP_TRANSPORT", raising=False)
        assert _select_transport() == "stdio"

    def test_reads_http_from_env(self, monkeypatch):
        monkeypatch.setenv("MCP_TRANSPORT", "http")
        assert _select_transport() == "http"

    def test_is_case_insensitive(self, monkeypatch):
        monkeypatch.setenv("MCP_TRANSPORT", "HTTP")
        assert _select_transport() == "http"

    def test_rejects_unknown_value(self, monkeypatch):
        monkeypatch.setenv("MCP_TRANSPORT", "carrier-pigeon")
        with pytest.raises(ValueError, match="carrier-pigeon"):
            _select_transport()


class TestHttpApp:
    def test_ping_returns_ok(self):
        from starlette.testclient import TestClient

        client = TestClient(_build_http_app())
        response = client.get("/ping")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_mcp_endpoint_is_mounted(self):
        app = _build_http_app()
        mounted_paths = {getattr(route, "path", None) for route in app.routes}
        assert "/mcp" in mounted_paths

    def test_mcp_endpoint_handles_bare_path_without_redirect_or_404(self):
        """Starlette's Mount redirects "/mcp" -> "/mcp/" by default (and
        its path regex doesn't even match the bare path without a
        redirect), but MCP streamable-HTTP clients POST to the exact
        configured URL and don't necessarily follow redirects -- this must
        actually reach the MCP session manager, not bounce or 404."""
        from starlette.testclient import TestClient

        # The session manager's task group is only created by the app's
        # lifespan ("startup" event) -- TestClient only runs that as a
        # context manager, not on bare instantiation.
        with TestClient(_build_http_app()) as client:
            response = client.post(
                "/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "test", "version": "0"},
                    },
                },
                headers={"Accept": "application/json, text/event-stream"},
                follow_redirects=False,
            )

        assert response.status_code == 200
        assert response.json()["result"]["serverInfo"]["name"] == server.name
