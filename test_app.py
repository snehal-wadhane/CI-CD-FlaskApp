import pytest
from app import create_app


# ── Fixture ───────────────────────────────────────────────────
@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client


# ══════════════════════════════════════════════════════════════
# 1. SMOKE TEST — app starts at all
# ══════════════════════════════════════════════════════════════
def test_app_created():
    """App factory returns a valid Flask app."""
    app = create_app()
    assert app is not None


# ══════════════════════════════════════════════════════════════
# 2. ROUTE TESTS
# ══════════════════════════════════════════════════════════════
def test_home_get_returns_200(client):
    """GET / returns 200 OK."""
    response = client.get('/')
    assert response.status_code == 200


def test_home_post_returns_200(client):
    """POST / returns 200 OK."""
    response = client.post('/')
    assert response.status_code == 200


def test_home_returns_html(client):
    """/ returns HTML content."""
    response = client.get('/')
    assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data


def test_404_on_unknown_route(client):
    """Unknown route returns 404."""
    response = client.get('/this-page-does-not-exist')
    assert response.status_code == 404


# ══════════════════════════════════════════════════════════════
# 3. CONTENT TESTS
# ══════════════════════════════════════════════════════════════
def test_home_page_not_empty(client):
    """Home page response body is not empty."""
    response = client.get('/')
    assert len(response.data) > 0


def test_response_content_type_is_html(client):
    """Response content-type is text/html."""
    response = client.get('/')
    assert 'text/html' in response.content_type


# ══════════════════════════════════════════════════════════════
# 4. APP CONFIG TESTS
# ══════════════════════════════════════════════════════════════
def test_testing_mode_enabled(client):
    """Testing flag is True during tests."""
    app = create_app()
    app.config['TESTING'] = True
    assert app.config['TESTING'] is True


def test_app_has_home_route():
    """App has a route registered for '/'."""
    app = create_app()
    rules = [str(rule) for rule in app.url_map.iter_rules()]
    assert '/' in rules


def test_home_route_allows_get():
    """Home route accepts GET method."""
    app = create_app()
    for rule in app.url_map.iter_rules():
        if str(rule) == '/':
            assert 'GET' in rule.methods


def test_home_route_allows_post():
    """Home route accepts POST method."""
    app = create_app()
    for rule in app.url_map.iter_rules():
        if str(rule) == '/':
            assert 'POST' in rule.methods