"""
FAILURE DEMONSTRATION TESTS
============================
These tests show what happens when things go WRONG at each phase.
Run normally → all pass (green pipeline)
Uncomment a BREAK line → that phase fails (red pipeline)

Usage for presentation:
  Phase 1 demo: uncomment BREAK_BUILD    → Build phase fails
  Phase 2 demo: uncomment BREAK_TEST     → Test phase fails  
  Phase 3 demo: uncomment BREAK_DEPLOY   → Deploy check fails
"""

import json
import os
import sys
import pytest
from app import app, uptime_str, get_disk


# ── Fixture ───────────────────────────────────────────────────
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ══════════════════════════════════════════════════════════════
# PHASE 1 — BUILD FAILURES
# What can go wrong: missing imports, syntax errors, wrong Python version
# ══════════════════════════════════════════════════════════════
class TestBuildPhase:

    def test_all_imports_available(self):
        """All required modules are importable — catches missing packages."""
        import flask
        import psutil
        import platform
        import os, sys, time
        from datetime import datetime, timezone
        assert True  # If we reach here, all imports succeeded

    def test_python_version_compatible(self):
        """Python version is 3.8 or higher — catches wrong base image."""
        major, minor = sys.version_info.major, sys.version_info.minor
        assert major == 3, f"Expected Python 3, got {major}"
        assert minor >= 8, f"Expected Python 3.8+, got 3.{minor}"

    def test_flask_version_compatible(self):
        """Flask version is 2.x or higher."""
        import importlib.metadata
        version = importlib.metadata.version("flask")
        major = int(version.split(".")[0])
        assert major >= 2, f"Flask 2+ required, found {version}"

    def test_app_module_loads_without_error(self):
        """app.py imports cleanly — catches syntax errors."""
        import importlib
        spec = importlib.util.spec_from_file_location("app", "app.py")
        assert spec is not None, "app.py not found in project root"

    def test_psutil_can_read_system(self):
        """psutil works in this environment — catches Alpine Linux issues."""
        import psutil
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        assert isinstance(cpu, float)
        assert mem.total > 0

    # ── TO DEMO BUILD FAILURE: uncomment the line below ──────
    # def test_BREAK_BUILD_missing_package(self):
    #     """DEMO: simulates a missing package breaking the build."""
    #     import non_existent_package_xyz   # ImportError → build fails


# ══════════════════════════════════════════════════════════════
# PHASE 2 — TEST FAILURES
# What can go wrong: wrong response, broken route, bad JSON
# ══════════════════════════════════════════════════════════════
class TestTestPhase:

    # ── Home route ────────────────────────────────────────────
    def test_home_returns_200(self, client):
        """GET / must return 200 — fails if route is broken."""
        res = client.get("/")
        assert res.status_code == 200, \
            f"Expected 200, got {res.status_code}. Home route is broken!"

    def test_home_returns_html(self, client):
        """/ must return HTML — fails if template is missing."""
        res = client.get("/")
        assert b"html" in res.data.lower(), \
            "Home page returned no HTML. Template may be missing!"

    # ── Health route ──────────────────────────────────────────
    def test_health_returns_200(self, client):
        """GET /health must return 200."""
        res = client.get("/health")
        assert res.status_code == 200, \
            f"Health check failed! Got {res.status_code}"

    def test_health_status_is_healthy(self, client):
        """Health check must return {status: healthy}."""
        data = json.loads(client.get("/health").data)
        assert data.get("status") == "healthy", \
            f"Health check returned wrong status: {data.get('status')}"

    # ── Status route ──────────────────────────────────────────
    def test_status_returns_200(self, client):
        """GET /api/status must return 200."""
        res = client.get("/api/status")
        assert res.status_code == 200

    def test_status_is_online(self, client):
        """Status must report online."""
        data = json.loads(client.get("/api/status").data)
        assert data["status"] == "online", \
            f"App reported status='{data['status']}' instead of 'online'"

    def test_cpu_percent_valid_range(self, client):
        """CPU percent must be between 0-100."""
        data = json.loads(client.get("/api/status").data)
        cpu  = data["cpu_percent"]
        assert 0 <= cpu <= 100, \
            f"CPU percent out of range: {cpu}"

    def test_memory_used_less_than_total(self, client):
        """Memory used cannot exceed total — catches psutil bug."""
        data = json.loads(client.get("/api/status").data)
        mem  = data["memory"]
        assert mem["used_mb"] <= mem["total_mb"], \
            f"Memory used ({mem['used_mb']}MB) > total ({mem['total_mb']}MB)!"

    def test_disk_used_less_than_total(self, client):
        """Disk used cannot exceed total."""
        data = json.loads(client.get("/api/status").data)
        disk = data["disk"]
        assert disk["used_gb"] <= disk["total_gb"], \
            f"Disk used ({disk['used_gb']}GB) > total ({disk['total_gb']}GB)!"

    def test_timestamp_is_utc(self, client):
        """Timestamp must be UTC ISO format."""
        data = json.loads(client.get("/api/status").data)
        ts   = data["timestamp"]
        assert ts.endswith("+00:00") or ts.endswith("Z"), \
            f"Timestamp not in UTC: {ts}"

    def test_deployment_version_set(self, client):
        """APP_VERSION env var must be set or default to 1.0.0."""
        data    = json.loads(client.get("/api/status").data)
        version = data["deployment"]["version"]
        assert version != "", "APP_VERSION is empty!"
        assert version == os.environ.get("APP_VERSION", "1.0.0")

    def test_no_500_errors(self, client):
        """None of the routes should return 500 (server error)."""
        for route in ["/", "/health", "/api/status"]:
            res = client.get(route)
            assert res.status_code != 500, \
                f"Route {route} returned 500 Internal Server Error!"

    def test_unknown_route_is_404_not_500(self, client):
        """Unknown routes must 404, not crash with 500."""
        res = client.get("/totally-broken-route")
        assert res.status_code == 404, \
            f"Expected 404 for unknown route, got {res.status_code}"

    # ── TO DEMO TEST FAILURE: uncomment one block below ───────

    # def test_BREAK_wrong_health_status(self, client):
    #     """DEMO: expects wrong value — will always fail."""
    #     data = json.loads(client.get("/health").data)
    #     assert data["status"] == "unhealthy", \
    #         f"DEMO FAILURE: health check caught wrong value '{data['status']}'"

    # def test_BREAK_home_returns_404(self, client):
    #     """DEMO: expects 404 from home — will always fail."""
    #     res = client.get("/")
    #     assert res.status_code == 404, \
    #         f"DEMO FAILURE: Expected 404 but got {res.status_code}"

    # def test_BREAK_cpu_impossible_value(self, client):
    #     """DEMO: expects CPU > 100 — impossible, always fails."""
    #     data = json.loads(client.get("/api/status").data)
    #     assert data["cpu_percent"] > 100, \
    #         f"DEMO FAILURE: CPU was {data['cpu_percent']}%, expected > 100%"


# ══════════════════════════════════════════════════════════════
# PHASE 3 — DEPLOY READINESS CHECKS
# What can go wrong: wrong env vars, missing files, wrong port
# ══════════════════════════════════════════════════════════════
class TestDeployPhase:

    def test_dockerfile_exists(self):
        """Dockerfile must exist in project root."""
        assert os.path.exists("Dockerfile"), \
            "Dockerfile not found! Cannot build Docker image."

    def test_requirements_txt_exists(self):
        """requirements.txt must exist."""
        assert os.path.exists("requirements.txt"), \
            "requirements.txt not found! pip install will fail."

    def test_requirements_has_flask(self):
        """requirements.txt must include Flask."""
        content = open("requirements.txt").read().lower()
        assert "flask" in content, \
            "Flask not listed in requirements.txt!"

    def test_requirements_has_psutil(self):
        """requirements.txt must include psutil."""
        content = open("requirements.txt").read().lower()
        assert "psutil" in content, \
            "psutil not in requirements.txt — app will crash on import!"

    def test_templates_folder_exists(self):
        """templates/ folder must exist for render_template to work."""
        assert os.path.isdir("templates"), \
            "templates/ folder missing — render_template will raise TemplateNotFound!"

    def test_index_template_exists(self):
        """templates/index.html must exist."""
        assert os.path.exists("templates/index.html"), \
            "templates/index.html missing — GET / will crash with 500!"

    def test_app_binds_correct_host(self):
        """App must bind to 0.0.0.0 to be reachable inside Kubernetes pod."""
        source = open("app.py").read()
        assert "0.0.0.0" in source, \
            "App does not bind to 0.0.0.0! Not reachable inside K8s pod."

    def test_app_runs_on_port_5000(self):
        """App must run on port 5000 to match K8s service.yml."""
        source = open("app.py").read()
        assert "5000" in source, \
            "Port 5000 not found in app.py. K8s service.yml expects port 5000!"

    def test_deployment_manifest_exists(self):
        """manifests/deployment.yml must exist for kubectl apply."""
        assert os.path.exists("manifests/deployment.yml"), \
            "manifests/deployment.yml missing — k8s-deploy step will fail!"

    def test_service_manifest_exists(self):
        """manifests/service.yml must exist."""
        assert os.path.exists("manifests/service.yml"), \
            "manifests/service.yml missing — LoadBalancer will not be created!"

    def test_no_hardcoded_secrets_in_app(self):
        """app.py must not contain hardcoded passwords or tokens."""
        source   = open("app.py").read().lower()
        bad_keys = ["password=", "secret_key=", "api_key=", "token="]
        for key in bad_keys:
            assert key not in source, \
                f"Hardcoded secret found in app.py: '{key}' — security risk!"

    # ── TO DEMO DEPLOY FAILURE: uncomment one block below ─────

    # def test_BREAK_missing_dockerfile(self):
    #     """DEMO: pretends Dockerfile is missing."""
    #     assert os.path.exists("Dockerfile_missing"), \
    #         "DEMO FAILURE: Dockerfile not found — Docker build would fail!"

    # def test_BREAK_wrong_port(self):
    #     """DEMO: expects port 8080 but app uses 5000."""
    #     source = open("app.py").read()
    #     assert "8080" in source, \
    #         "DEMO FAILURE: App not on port 8080 — K8s service mismatch!"