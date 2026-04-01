import pytest
import app as app_module


# ── Detect app pattern and create client ──────────────────────
def get_app():
    """Works with both app patterns:
       Pattern 1: app = Flask(__name__)  (direct)
       Pattern 2: def create_app(): ...  (factory)
    """
    if hasattr(app_module, 'create_app'):
        flask_app = app_module.create_app()
    elif hasattr(app_module, 'app'):
        flask_app = app_module.app
    else:
        raise RuntimeError("Could not find Flask app in app.py")
    return flask_app


@pytest.fixture
def client():
    flask_app = get_app()
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    with flask_app.test_client() as c:
        yield c


# ══════════════════════════════════════════════════════════════
# 1. SMOKE TESTS
# ══════════════════════════════════════════════════════════════
def test_app_loads():
    """App loads without errors."""
    flask_app = get_app()
    assert flask_app is not None


def test_app_is_flask_instance():
    """Loaded object is a Flask app."""
    from flask import Flask
    flask_app = get_app()
    assert isinstance(flask_app, Flask)


def test_app_has_routes():
    """App has at least one route registered."""
    flask_app = get_app()
    rules = [str(r) for r in flask_app.url_map.iter_rules()]
    assert len(rules) > 0


# ══════════════════════════════════════════════════════════════
# 2. HOME ROUTE TESTS
# ══════════════════════════════════════════════════════════════
def test_home_get_200(client):
    """GET / returns 200 OK."""
    res = client.get('/')
    assert res.status_code == 200


def test_home_post_200(client):
    """POST / returns 200 OK."""
    res = client.post('/')
    assert res.status_code == 200


def test_home_returns_html(client):
    """/ returns HTML content."""
    res = client.get('/')
    assert b'<html' in res.data.lower() or b'<!doctype' in res.data.lower()


def test_home_not_empty(client):
    """Home page has content."""
    res = client.get('/')
    assert len(res.data) > 0


def test_home_content_type_html(client):
    """Response content-type is text/html."""
    res = client.get('/')
    assert 'text/html' in res.content_type


# ══════════════════════════════════════════════════════════════
# 3. 404 TEST
# ══════════════════════════════════════════════════════════════
def test_404_on_unknown_route(client):
    """Unknown route returns 404."""
    res = client.get('/this-route-does-not-exist-xyz')
    assert res.status_code == 404


# ══════════════════════════════════════════════════════════════
# 4. CONFIG TESTS
# ══════════════════════════════════════════════════════════════
def test_testing_config():
    """Testing mode can be enabled."""
    flask_app = get_app()
    flask_app.config['TESTING'] = True
    assert flask_app.config['TESTING'] is True


def test_home_route_registered():
    """'/' route exists in URL map."""
    flask_app = get_app()
    rules = [str(r) for r in flask_app.url_map.iter_rules()]
    assert '/' in rules