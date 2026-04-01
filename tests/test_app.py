"""
tests/test_app.py
Unit + integration tests for the Flask application.
Run locally:  pytest tests/ -v
"""

import json
import pytest
from app import app


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    """Return a test client with testing mode enabled."""
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ── Route: GET / ──────────────────────────────────────────────────────────────

class TestIndexRoute:
    def test_index_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_index_returns_html(self, client):
        response = client.get("/")
        assert b"<!DOCTYPE html>" in response.data or b"<html" in response.data


# ── Route: GET /health ────────────────────────────────────────────────────────

class TestHealthRoute:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        response = client.get("/health")
        assert response.content_type == "application/json"

    def test_health_body(self, client):
        response = client.get("/health")
        data = json.loads(response.data)
        assert data.get("status") == "healthy"


# ── Route: GET /api/status ────────────────────────────────────────────────────

class TestApiStatusRoute:
    def test_status_returns_200(self, client):
        response = client.get("/api/status")
        assert response.status_code == 200

    def test_status_returns_json(self, client):
        response = client.get("/api/status")
        assert response.content_type == "application/json"

    def test_status_top_level_keys(self, client):
        response = client.get("/api/status")
        data = json.loads(response.data)
        expected_keys = {"status", "uptime", "timestamp", "system",
                         "cpu_percent", "memory", "disk", "deployment"}
        assert expected_keys.issubset(data.keys())

    def test_status_value(self, client):
        response = client.get("/api/status")
        data = json.loads(response.data)
        assert data["status"] == "online"

    def test_status_system_keys(self, client):
        response = client.get("/api/status")
        data = json.loads(response.data)
        system = data.get("system", {})
        assert {"os", "python", "hostname"}.issubset(system.keys())

    def test_status_memory_keys(self, client):
        response = client.get("/api/status")
        data = json.loads(response.data)
        mem = data.get("memory", {})
        assert {"total_mb", "used_mb", "percent"}.issubset(mem.keys())

    def test_status_disk_keys(self, client):
        response = client.get("/api/status")
        data = json.loads(response.data)
        disk = data.get("disk", {})
        assert {"total_gb", "used_gb", "percent"}.issubset(disk.keys())

    def test_status_deployment_keys(self, client):
        response = client.get("/api/status")
        data = json.loads(response.data)
        dep = data.get("deployment", {})
        assert {"env", "version", "region"}.issubset(dep.keys())

    def test_uptime_format(self, client):
        """Uptime string should match pattern like '0h 0m 5s'."""
        import re
        response = client.get("/api/status")
        data = json.loads(response.data)
        assert re.match(r"\d+h \d+m \d+s", data["uptime"])

    def test_cpu_percent_is_numeric(self, client):
        response = client.get("/api/status")
        data = json.loads(response.data)
        assert isinstance(data["cpu_percent"], (int, float))

    def test_memory_percent_in_range(self, client):
        response = client.get("/api/status")
        data = json.loads(response.data)
        percent = data["memory"]["percent"]
        assert 0 <= percent <= 100

    def test_disk_percent_in_range(self, client):
        response = client.get("/api/status")
        data = json.loads(response.data)
        percent = data["disk"]["percent"]
        assert 0 <= percent <= 100


# ── Edge cases ────────────────────────────────────────────────────────────────

class TestEdgeCases:
    def test_unknown_route_returns_404(self, client):
        response = client.get("/this-does-not-exist")
        assert response.status_code == 404

    def test_post_to_health_not_allowed(self, client):
        response = client.post("/health")
        # Flask returns 405 for disallowed methods
        assert response.status_code == 405