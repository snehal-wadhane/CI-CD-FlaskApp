import json
import pytest
from app import app, uptime_str, get_disk


# ── Fixture ───────────────────────────────────────────────────
@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as c:
        yield c


# ══════════════════════════════════════════════════════════════
# 1. SMOKE TESTS
# ══════════════════════════════════════════════════════════════
def test_app_loads():
    """Flask app object exists and is configured."""
    assert app is not None


def test_app_has_three_routes():
    """App has /, /health, /api/status registered."""
    rules = [str(r) for r in app.url_map.iter_rules()]
    assert "/"            in rules
    assert "/health"      in rules
    assert "/api/status"  in rules


# ══════════════════════════════════════════════════════════════
# 2. HOME ROUTE  /
# ══════════════════════════════════════════════════════════════
def test_home_returns_200(client):
    """GET / returns 200 OK."""
    res = client.get("/")
    assert res.status_code == 200


def test_home_returns_html(client):
    """GET / returns HTML content."""
    res = client.get("/")
    assert b"html" in res.data.lower()


def test_home_content_type(client):
    """GET / content-type is text/html."""
    res = client.get("/")
    assert "text/html" in res.content_type


# ══════════════════════════════════════════════════════════════
# 3. HEALTH ROUTE  /health
# ══════════════════════════════════════════════════════════════
def test_health_returns_200(client):
    """GET /health returns 200 OK."""
    res = client.get("/health")
    assert res.status_code == 200


def test_health_returns_json(client):
    """GET /health returns JSON."""
    res = client.get("/health")
    assert res.content_type == "application/json"


def test_health_status_value(client):
    """GET /health returns {status: healthy}."""
    res  = client.get("/health")
    data = json.loads(res.data)
    assert data["status"] == "healthy"


# ══════════════════════════════════════════════════════════════
# 4. STATUS ROUTE  /api/status
# ══════════════════════════════════════════════════════════════
def test_status_returns_200(client):
    """GET /api/status returns 200 OK."""
    res = client.get("/api/status")
    assert res.status_code == 200


def test_status_returns_json(client):
    """GET /api/status returns JSON."""
    res = client.get("/api/status")
    assert res.content_type == "application/json"


def test_status_value_is_online(client):
    """status field is 'online'."""
    data = json.loads(client.get("/api/status").data)
    assert data["status"] == "online"


def test_status_has_uptime(client):
    """Response contains uptime string."""
    data = json.loads(client.get("/api/status").data)
    assert "uptime" in data
    assert isinstance(data["uptime"], str)
    assert "h" in data["uptime"]


def test_status_has_timestamp(client):
    """Response contains ISO timestamp."""
    data = json.loads(client.get("/api/status").data)
    assert "timestamp" in data
    assert "T" in data["timestamp"]   # ISO 8601 format


def test_status_has_system_info(client):
    """Response contains system block with os, python, hostname."""
    data = json.loads(client.get("/api/status").data)
    assert "system" in data
    assert "os"       in data["system"]
    assert "python"   in data["system"]
    assert "hostname" in data["system"]


def test_status_cpu_is_number(client):
    """cpu_percent is a number between 0 and 100."""
    data = json.loads(client.get("/api/status").data)
    assert "cpu_percent" in data
    assert 0 <= data["cpu_percent"] <= 100


def test_status_memory_block(client):
    """Memory block has total_mb, used_mb, percent."""
    data = json.loads(client.get("/api/status").data)
    mem  = data["memory"]
    assert "total_mb" in mem
    assert "used_mb"  in mem
    assert "percent"  in mem
    assert mem["total_mb"] > 0
    assert 0 <= mem["percent"] <= 100


def test_status_disk_block(client):
    """Disk block has total_gb, used_gb, percent."""
    data = json.loads(client.get("/api/status").data)
    disk = data["disk"]
    assert "total_gb" in disk
    assert "used_gb"  in disk
    assert "percent"  in disk
    assert disk["total_gb"] > 0
    assert 0 <= disk["percent"] <= 100


def test_status_deployment_block(client):
    """Deployment block has env, version, region."""
    data = json.loads(client.get("/api/status").data)
    dep  = data["deployment"]
    assert "env"     in dep
    assert "version" in dep
    assert "region"  in dep


def test_deployment_defaults(client):
    """Default deployment values are correct."""
    data = json.loads(client.get("/api/status").data)
    dep  = data["deployment"]
    assert dep["version"] == "1.0.0"


# ══════════════════════════════════════════════════════════════
# 5. 404 TEST
# ══════════════════════════════════════════════════════════════
def test_unknown_route_404(client):
    """Unknown route returns 404."""
    res = client.get("/this-does-not-exist")
    assert res.status_code == 404


# ══════════════════════════════════════════════════════════════
# 6. HELPER FUNCTION TESTS
# ══════════════════════════════════════════════════════════════
def test_uptime_str_format():
    """uptime_str returns correct format like '0h 0m Xs'."""
    result = uptime_str()
    assert "h" in result
    assert "m" in result
    assert "s" in result


def test_get_disk_returns_data():
    """get_disk returns an object with total, used, percent."""
    disk = get_disk()
    assert disk.total > 0
    assert disk.used  > 0
    assert 0 <= disk.percent <= 100