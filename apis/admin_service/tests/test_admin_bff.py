"""Contract tests del BFF admin (espejo de api_gateway): login, auth, CSRF, proxy, métodos."""

import json
from unittest.mock import MagicMock, patch

import requests


def _mock_resp(json_data=None, status_code=200):
    m = MagicMock()
    m.status_code = status_code
    payload = json_data or {}
    m.json.return_value = payload
    m.content = json.dumps(payload).encode()
    m.headers = {"Content-Type": "application/json"}
    return m


def _login(client, usuario="admin", contra="x"):
    resp_mock = _mock_resp({
        "access_token": "auth-service-token",
        "refresh_token": "auth-refresh",
        "usuario": {"usuario": usuario},
    }, 200)
    with patch("app.routes.auth_routes.requests.post", return_value=resp_mock):
        r = client.post("/api/admin/auth/login", json={"usuario": usuario, "contraseña": contra})
    assert r.status_code == 200, r.get_json()
    body = r.get_json()
    return body["access_token"], body["csrf_token"]


def _headers(token, csrf=None):
    h = {"Authorization": f"Bearer {token}"}
    if csrf:
        h["X-CSRF-Token"] = csrf
    return h


# ── login ────────────────────────────────────────────────────────────────────
def test_login_sin_body(client):
    assert client.post("/api/admin/auth/login").status_code == 400


def test_login_ok_returns_tokens(client):
    token, csrf = _login(client)
    assert token and len(token) > 20
    assert csrf and len(csrf) == 64


def test_login_auth_service_401(client):
    with patch("app.routes.auth_routes.requests.post", return_value=_mock_resp({"errors": ["bad"]}, 401)):
        r = client.post("/api/admin/auth/login", json={"usuario": "x", "contraseña": "y"})
    assert r.status_code == 401


def test_login_connection_error_503(client):
    with patch("app.routes.auth_routes.requests.post", side_effect=requests.exceptions.ConnectionError()):
        r = client.post("/api/admin/auth/login", json={"usuario": "x", "contraseña": "y"})
    assert r.status_code == 503


# ── auth / csrf de borde ───────────────────────────────────────────────────────
def test_protected_without_jwt_401(client):
    assert client.get("/api/admin/usuario/").status_code == 401
    assert client.get("/api/admin/empresa/").status_code == 401
    assert client.get("/api/admin/cargo/").status_code == 401


def test_write_without_csrf_403(client):
    token, _ = _login(client)
    r = client.post("/api/admin/usuario/", json={"nombre": "x"}, headers=_headers(token))
    assert r.status_code == 403


def test_logout_requires_csrf(client):
    token, _ = _login(client)
    assert client.post("/api/admin/auth/logout", headers=_headers(token)).status_code == 403


def test_logout_ok(client):
    token, csrf = _login(client)
    r = client.post("/api/admin/auth/logout", headers=_headers(token, csrf))
    assert r.status_code == 200


# ── proxy forwarding ───────────────────────────────────────────────────────────
def test_get_proxies_to_auth_service(client):
    token, _ = _login(client)
    with patch("app.utils.proxy.requests.request", return_value=_mock_resp({"data": []})) as m:
        r = client.get("/api/admin/usuario/", headers=_headers(token))
    assert r.status_code == 200
    assert m.call_args[0][1] == "http://auth.test/usuario/"
    assert m.call_args[1]["headers"]["X-Internal-Service-Secret"] == "test-internal-secret"


def test_get_by_oid_proxies_to_catalogues(client):
    token, _ = _login(client)
    with patch("app.utils.proxy.requests.request", return_value=_mock_resp({"oid": "1"})) as m:
        r = client.get("/api/admin/empresa/1", headers=_headers(token))
    assert r.status_code == 200
    assert m.call_args[0][1] == "http://catalogues.test/empresa/1"


def test_create_sanitizes_and_proxies(client):
    token, csrf = _login(client)
    captured = {}

    def fake(method, url, **kw):
        captured["json"] = kw.get("json")
        captured["url"] = url
        return _mock_resp({"oid": "n"}, 201)

    with patch("app.utils.proxy.requests.request", side_effect=fake):
        r = client.post("/api/admin/sucursal/", json={"nombre": "<script>x</script>Suc"},
                        headers=_headers(token, csrf))
    assert r.status_code == 201
    assert "<script>" not in captured["json"]["nombre"]
    assert captured["url"] == "http://catalogues.test/sucursal/"


def test_proxy_connection_error_503(client):
    token, _ = _login(client)
    with patch("app.utils.proxy.requests.request", side_effect=requests.exceptions.ConnectionError()):
        r = client.get("/api/admin/cargo/", headers=_headers(token))
    assert r.status_code == 503


def test_list_endpoint_is_read_only_no_csrf(client):
    token, _ = _login(client)
    with patch("app.utils.proxy.requests.request", return_value=_mock_resp([])) as m:
        r = client.post("/api/admin/usuario/list", json={"oid_list": ["a"]}, headers=_headers(token))
    assert r.status_code == 200  # /list no exige CSRF (es lectura)
    assert m.call_args[0][1] == "http://auth.test/usuario/list"


# ── métodos ────────────────────────────────────────────────────────────────────
def test_method_not_allowed(client):
    token, csrf = _login(client)
    r = client.patch("/api/admin/usuario/", json={}, headers=_headers(token, csrf))
    assert r.status_code == 405
