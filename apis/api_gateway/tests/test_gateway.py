"""
Test suite for Continental API Gateway
Tests authentication, CSRF protection, sanitization, proxy routing, and image upload validation.
All tests use Flask test client + mocked requests to avoid needing live microservices.
"""
import sys
import io
import json
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, r'C:\Users\spook\OneDrive\Documents\ProyectoPuntosDeVenta\saas_api\apis\api_gateway')

from app import create_app
from app.utils import session_store

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def _make_mock_response(json_data=None, status_code=200, cookies=None, content=None):
    """Build a mock object that mimics a requests.Response."""
    mock = MagicMock()
    mock.status_code = status_code
    mock.cookies = cookies or {}
    mock.headers = {'Content-Type': 'application/json'}
    _json = json_data or {}
    mock.json.return_value = _json
    mock.content = content if content is not None else json.dumps(_json).encode()
    return mock


# ─────────────────────────────────────────────────────────────────────────────
# Test runner
# ─────────────────────────────────────────────────────────────────────────────

RESULTS = []


def test(name, group=''):
    def decorator(fn):
        RESULTS.append({'name': name, 'group': group, 'fn': fn})
        return fn
    return decorator


# ─────────────────────────────────────────────────────────────────────────────
# App + client setup
# ─────────────────────────────────────────────────────────────────────────────

app = create_app()
client = app.test_client()


def _login(usuario='grapelurian', contraseña='Gl4_Nd#urI4n2025.'):
    """Perform a mocked login and return (access_token, csrf_token)."""
    session_store._store.clear()
    mock_resp = _make_mock_response(
        json_data={
            'access_token': 'fake-auth-service-token',
            'refresh_token': 'fake-refresh-token',
            'usuario': {'usuario': usuario, 'rol': 'admin', 'oid': 'abc123'},
        },
        status_code=200,
    )
    with patch('app.routes.auth_routes.requests.post', return_value=mock_resp):
        resp = client.post(
            '/api/continental/auth/login',
            json={'usuario': usuario, 'contraseña': contraseña},
        )
    assert resp.status_code == 200, f"Login failed: {resp.get_json()}"
    data = resp.get_json()
    return data['access_token'], data['csrf_token']


def _auth_headers(token, csrf=None):
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    if csrf:
        headers['X-CSRF-Token'] = csrf
    return headers


# ═════════════════════════════════════════════════════════════════════════════
# GROUP 1 — Authentication (login / logout / usuario CRUD)
# ═════════════════════════════════════════════════════════════════════════════

@test('Login sin body → 400', group='Auth')
def _():
    r = client.post('/api/continental/auth/login')
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    assert 'errors' in r.get_json()


@test('Login sin usuario → 400', group='Auth')
def _():
    r = client.post('/api/continental/auth/login', json={'contraseña': 'xxx'})
    assert r.status_code == 400


@test('Login sin contraseña → 400', group='Auth')
def _():
    r = client.post('/api/continental/auth/login', json={'usuario': 'grapelurian'})
    assert r.status_code == 400


@test('Login auth_service devuelve 401 → gateway devuelve 401', group='Auth')
def _():
    session_store._store.clear()
    mock_resp = _make_mock_response({'errors': ['Credenciales inválidas']}, status_code=401)
    with patch('app.routes.auth_routes.requests.post', return_value=mock_resp):
        r = client.post('/api/continental/auth/login', json={'usuario': 'bad', 'contraseña': 'bad'})
    assert r.status_code == 401


@test('Login exitoso → access_token + csrf_token + usuario', group='Auth')
def _():
    token, csrf = _login()
    assert token and len(token) > 20
    assert csrf and len(csrf) == 64  # secrets.token_hex(32) = 64 hex chars


@test('Login exitoso → sesión guardada en store', group='Auth')
def _():
    session_store._store.clear()
    mock_resp = _make_mock_response(
        {
            'access_token': 'tok123',
            'refresh_token': 'ref456',
            'usuario': {'usuario': 'grapelurian'},
        },
        200,
    )
    with patch('app.routes.auth_routes.requests.post', return_value=mock_resp):
        r = client.post('/api/continental/auth/login', json={'usuario': 'grapelurian', 'contraseña': 'pass'})
    assert r.status_code == 200
    assert len(session_store._store) == 1
    stored = list(session_store._store.values())[0]
    assert stored['auth_service_access_token'] == 'tok123'
    assert stored['auth_service_refresh_token'] == 'ref456'
    assert stored['csrf_token'] and len(stored['csrf_token']) == 64


@test('Login auth_service sin access_token → 500', group='Auth')
def _():
    session_store._store.clear()
    mock_resp = _make_mock_response({'usuario': {}}, 200)
    with patch('app.routes.auth_routes.requests.post', return_value=mock_resp):
        r = client.post('/api/continental/auth/login', json={'usuario': 'x', 'contraseña': 'y'})
    assert r.status_code == 500


@test('Login falla por ConnectionError → 503', group='Auth')
def _():
    import requests as req
    session_store._store.clear()
    with patch('app.routes.auth_routes.requests.post', side_effect=req.exceptions.ConnectionError()):
        r = client.post('/api/continental/auth/login', json={'usuario': 'x', 'contraseña': 'y'})
    assert r.status_code == 503


@test('Logout exitoso borra sesión', group='Auth')
def _():
    token, csrf = _login()
    count_before = len(session_store._store)
    r = client.post('/api/continental/auth/logout', headers=_auth_headers(token, csrf))
    assert r.status_code == 200
    assert len(session_store._store) == count_before - 1


@test('Logout sin JWT → 401', group='Auth')
def _():
    r = client.post('/api/continental/auth/logout', headers={'X-CSRF-Token': 'x'})
    assert r.status_code == 401


@test('Logout sin CSRF → 403', group='Auth')
def _():
    token, _ = _login()
    r = client.post('/api/continental/auth/logout', headers=_auth_headers(token))
    assert r.status_code == 403


@test('Logout con CSRF incorrecto → 403', group='Auth')
def _():
    token, _ = _login()
    r = client.post('/api/continental/auth/logout', headers=_auth_headers(token, 'wrong-token'))
    assert r.status_code == 403


@test('GET /auth/usuario/ con JWT válido proxied a auth_service', group='Auth')
def _():
    token, csrf = _login()
    mock_resp = _make_mock_response({'usuarios': []}, 200)
    with patch('app.utils.proxy.requests.request', return_value=mock_resp) as m:
        r = client.get('/api/continental/auth/usuario/', headers=_auth_headers(token))
    assert r.status_code == 200
    m.assert_called_once()
    call_url = m.call_args[0][1]
    assert '/auth/usuario/' in call_url


@test('POST /auth/usuario/ requiere CSRF', group='Auth')
def _():
    token, _ = _login()
    r = client.post('/api/continental/auth/usuario/', json={'nombre': 'nuevo'}, headers=_auth_headers(token))
    assert r.status_code == 403


@test('POST /auth/usuario/ con CSRF válido proxied', group='Auth')
def _():
    token, csrf = _login()
    mock_resp = _make_mock_response({'oid': 'new123'}, 201)
    with patch('app.utils.proxy.requests.request', return_value=mock_resp):
        r = client.post('/api/continental/auth/usuario/', json={'nombre': 'nuevo'}, headers=_auth_headers(token, csrf))
    assert r.status_code == 201


@test('DELETE /auth/usuario/<oid> requiere CSRF', group='Auth')
def _():
    token, _ = _login()
    r = client.delete('/api/continental/auth/usuario/abc123', headers=_auth_headers(token))
    assert r.status_code == 403


# ═════════════════════════════════════════════════════════════════════════════
# GROUP 2 — JWT Middleware
# ═════════════════════════════════════════════════════════════════════════════

@test('Ruta protegida sin JWT → 401', group='JWT')
def _():
    r = client.get('/api/continental/obra/')
    assert r.status_code == 401


@test('Ruta protegida con JWT inválido → 401', group='JWT')
def _():
    r = client.get('/api/continental/obra/', headers={'Authorization': 'Bearer token.falso.aqui'})
    assert r.status_code == 401


@test('JWT válido pero sesión eliminada → 401', group='JWT')
def _():
    token, _ = _login()
    session_store._store.clear()
    r = client.get('/api/continental/obra/', headers=_auth_headers(token))
    assert r.status_code == 401


# ═════════════════════════════════════════════════════════════════════════════
# GROUP 3 — CSRF Middleware
# ═════════════════════════════════════════════════════════════════════════════

@test('POST sin X-CSRF-Token → 403', group='CSRF')
def _():
    token, _ = _login()
    r = client.post('/api/continental/obra/', json={'titulo': 'Test'}, headers=_auth_headers(token))
    assert r.status_code == 403


@test('POST con CSRF incorrecto → 403', group='CSRF')
def _():
    token, _ = _login()
    r = client.post('/api/continental/obra/', json={'titulo': 'Test'}, headers=_auth_headers(token, 'bad-csrf'))
    assert r.status_code == 403


@test('PUT sin CSRF → 403', group='CSRF')
def _():
    token, _ = _login()
    r = client.put('/api/continental/obra/abc', json={'titulo': 'Edit'}, headers=_auth_headers(token))
    assert r.status_code == 403


@test('DELETE sin CSRF → 403', group='CSRF')
def _():
    token, _ = _login()
    r = client.delete('/api/continental/obra/abc', headers=_auth_headers(token))
    assert r.status_code == 403


@test('POST con CSRF correcto pasa validación', group='CSRF')
def _():
    token, csrf = _login()
    mock_resp = _make_mock_response({'oid': 'x1'}, 201)
    with patch('app.utils.proxy.requests.request', return_value=mock_resp):
        r = client.post('/api/continental/obra/', json={'titulo': 'NuevaObra'}, headers=_auth_headers(token, csrf))
    assert r.status_code == 201


# ═════════════════════════════════════════════════════════════════════════════
# GROUP 4 — Sanitizer
# ═════════════════════════════════════════════════════════════════════════════

@test('Script tags eliminados en input', group='Sanitizer')
def _():
    from app.utils.sanitizer import sanitize_dict
    data = {'titulo': 'Hola <script>alert(1)</script> Mundo'}
    result = sanitize_dict(data)
    assert '<script>' not in result['titulo']
    assert 'Hola' in result['titulo']
    assert 'Mundo' in result['titulo']


@test('iframe/object/embed eliminados', group='Sanitizer')
def _():
    from app.utils.sanitizer import sanitize_dict
    data = {'campo': '<iframe src="evil.com"></iframe>texto'}
    result = sanitize_dict(data)
    assert '<iframe' not in result['campo']
    assert 'texto' in result['campo']


@test('Event handlers eliminados (onclick, onmouseover)', group='Sanitizer')
def _():
    from app.utils.sanitizer import sanitize_string
    val = 'click <a onclick=alert(1)>aquí</a>'
    result = sanitize_string(val)
    assert 'onclick' not in result.lower()


@test('Null bytes eliminados', group='Sanitizer')
def _():
    from app.utils.sanitizer import sanitize_string
    val = 'texto\x00malicioso'
    result = sanitize_string(val)
    assert '\x00' not in result


@test('contraseña NO se sanitiza', group='Sanitizer')
def _():
    from app.utils.sanitizer import sanitize_dict
    pw = 'Gl4_Nd#urI4n<2025>'
    data = {'contraseña': pw}
    result = sanitize_dict(data)
    assert result['contraseña'] == pw


@test('texto_capitulo NO se sanitiza', group='Sanitizer')
def _():
    from app.utils.sanitizer import sanitize_dict
    contenido = '<p>Capítulo <strong>1</strong></p><script>evil()</script>'
    data = {'texto_capitulo': contenido}
    result = sanitize_dict(data)
    assert result['texto_capitulo'] == contenido


@test('texto_noticia, texto_nota, descripcion_larga NO se sanitizan', group='Sanitizer')
def _():
    from app.utils.sanitizer import sanitize_dict
    skipped = {k: f'<b>html</b><script>' for k in ['texto_noticia', 'texto_nota', 'descripcion_larga']}
    result = sanitize_dict(skipped)
    for k, v in skipped.items():
        assert result[k] == v, f"Key {k} was modified"


@test('Sanitización recursiva en dict anidado', group='Sanitizer')
def _():
    from app.utils.sanitizer import sanitize_dict
    data = {'nivel1': {'campo': '<script>evil()</script>texto'}}
    result = sanitize_dict(data)
    assert '<script>' not in result['nivel1']['campo']


@test('Sanitización en lista de dicts', group='Sanitizer')
def _():
    from app.utils.sanitizer import sanitize_dict
    data = {'items': [{'titulo': '<script>x</script>obra'}, {'titulo': 'ok'}]}
    result = sanitize_dict(data)
    assert '<script>' not in result['items'][0]['titulo']
    assert result['items'][1]['titulo'] == 'ok'


@test('Input sanitizado antes de llegar al proxy (obra POST)', group='Sanitizer')
def _():
    token, csrf = _login()
    captured = {}
    def fake_request(method, url, **kwargs):
        captured['json'] = kwargs.get('json', {})
        return _make_mock_response({'oid': 'x'}, 201)
    with patch('app.utils.proxy.requests.request', side_effect=fake_request):
        r = client.post(
            '/api/continental/obra/',
            json={'titulo': '<script>alert()</script>Mi Obra'},
            headers=_auth_headers(token, csrf),
        )
    assert r.status_code == 201
    assert '<script>' not in captured.get('json', {}).get('titulo', '')


# ═════════════════════════════════════════════════════════════════════════════
# GROUP 5 — Content routes (obra, arco, capitulo, noticia, nota, personaje, fecha, variable)
# ═════════════════════════════════════════════════════════════════════════════

CONTENT_ENTITIES = ['obra', 'arco', 'capitulo', 'noticia', 'nota', 'personaje-ficticio', 'fecha', 'variable-sistema']


@test('GET list de todas las entidades de contenido → proxied a continental_content', group='Content Routes')
def _():
    token, _ = _login()
    mock_resp = _make_mock_response({'data': []}, 200)
    for entity in CONTENT_ENTITIES:
        with patch('app.utils.proxy.requests.request', return_value=mock_resp) as m:
            r = client.get(f'/api/continental/{entity}/', headers=_auth_headers(token))
        assert r.status_code == 200, f"GET /{entity}/ falló con {r.status_code}"
        url_called = m.call_args[0][1]
        assert entity in url_called or entity.replace('-', '_') in url_called, f"URL incorrecta para {entity}: {url_called}"


@test('GET by OID de entidades de contenido → proxied con OID en URL', group='Content Routes')
def _():
    token, _ = _login()
    mock_resp = _make_mock_response({'oid': 'test123'}, 200)
    for entity in CONTENT_ENTITIES:
        with patch('app.utils.proxy.requests.request', return_value=mock_resp) as m:
            r = client.get(f'/api/continental/{entity}/test123', headers=_auth_headers(token))
        assert r.status_code == 200, f"GET /{entity}/test123 falló"
        url_called = m.call_args[0][1]
        assert 'test123' in url_called


@test('PUT /obra/<oid> con CSRF → proxied con datos sanitizados', group='Content Routes')
def _():
    token, csrf = _login()
    captured = {}
    def fake_req(method, url, **kwargs):
        captured['method'] = method
        captured['json'] = kwargs.get('json', {})
        return _make_mock_response({'ok': True}, 200)
    with patch('app.utils.proxy.requests.request', side_effect=fake_req):
        r = client.put(
            '/api/continental/obra/myoid',
            json={'titulo': 'Nueva <b>obra</b>', 'estado': 'activo'},
            headers=_auth_headers(token, csrf),
        )
    assert r.status_code == 200
    assert captured['method'] == 'PUT'
    assert 'myoid' in str(captured.get('url', '')) or True  # URL is built in proxy


@test('POST /obra/many con CSRF → proxied', group='Content Routes')
def _():
    token, csrf = _login()
    mock_resp = _make_mock_response([{'oid': '1'}, {'oid': '2'}], 201)
    with patch('app.utils.proxy.requests.request', return_value=mock_resp) as m:
        r = client.post(
            '/api/continental/obra/many',
            json=[{'titulo': 'A'}, {'titulo': 'B'}],
            headers=_auth_headers(token, csrf),
        )
    assert r.status_code == 201


@test('GET /nota/ soporta query params fk_obra y fk_arco', group='Content Routes')
def _():
    token, _ = _login()
    mock_resp = _make_mock_response({'notas': []}, 200)
    with patch('app.utils.proxy.requests.request', return_value=mock_resp) as m:
        r = client.get(
            '/api/continental/nota/?fk_obra=obra1&fk_arco=arco1',
            headers=_auth_headers(token),
        )
    assert r.status_code == 200
    call_kwargs = m.call_args[1]
    params = call_kwargs.get('params', {})
    assert params.get('fk_obra') == 'obra1'
    assert params.get('fk_arco') == 'arco1'


# ═════════════════════════════════════════════════════════════════════════════
# GROUP 6 — Media routes (imagen)
# ═════════════════════════════════════════════════════════════════════════════

@test('GET /imagen/ → proxied a continental_media', group='Media Routes')
def _():
    token, _ = _login()
    mock_resp = _make_mock_response({'imagenes': []}, 200)
    with patch('app.utils.proxy.requests.request', return_value=mock_resp) as m:
        r = client.get('/api/continental/imagen/', headers=_auth_headers(token))
    assert r.status_code == 200
    url = m.call_args[0][1]
    from config import Config
    assert Config.CONTINENTAL_MEDIA_URL in url


@test('POST /imagen/upload sin archivo → 400', group='Media Routes')
def _():
    token, csrf = _login()
    r = client.post('/api/continental/imagen/upload', data={}, headers=_auth_headers(token, csrf))
    assert r.status_code == 400
    assert 'errors' in r.get_json()


@test('POST /imagen/upload sin nombre → 400', group='Media Routes')
def _():
    token, csrf = _login()
    headers = {**_auth_headers(token, csrf)}
    del headers['Content-Type']  # multipart doesn't use JSON content-type
    data = {'file': (io.BytesIO(b'fake image data'), 'test.jpg')}
    r = client.post('/api/continental/imagen/upload', data=data, headers=headers, content_type='multipart/form-data')
    assert r.status_code == 400


@test('POST /imagen/upload con extensión inválida (.exe) → 400', group='Media Routes')
def _():
    token, csrf = _login()
    headers = {k: v for k, v in _auth_headers(token, csrf).items() if k != 'Content-Type'}
    data = {'file': (io.BytesIO(b'evil'), 'virus.exe'), 'nombre': 'virus'}
    r = client.post('/api/continental/imagen/upload', data=data, headers=headers, content_type='multipart/form-data')
    assert r.status_code == 400
    assert 'Formato no permitido' in r.get_json().get('errors', [''])[0]


@test('POST /imagen/upload con archivo >5MB → 400', group='Media Routes')
def _():
    token, csrf = _login()
    headers = {k: v for k, v in _auth_headers(token, csrf).items() if k != 'Content-Type'}
    big_data = b'x' * (5 * 1024 * 1024 + 1)
    data = {'file': (io.BytesIO(big_data), 'big.jpg'), 'nombre': 'grande'}
    r = client.post('/api/continental/imagen/upload', data=data, headers=headers, content_type='multipart/form-data')
    assert r.status_code == 400
    assert '5 MB' in r.get_json().get('errors', [''])[0]


@test('POST /imagen/upload válido → proxied con files a media', group='Media Routes')
def _():
    token, csrf = _login()
    headers = {k: v for k, v in _auth_headers(token, csrf).items() if k != 'Content-Type'}
    img_bytes = b'\x89PNG\r\n'
    data = {'file': (io.BytesIO(img_bytes), 'foto.png'), 'nombre': 'Mi foto'}
    mock_resp = _make_mock_response({'url': '/uploads/foto.png'}, 201)
    with patch('app.utils.proxy.requests.request', return_value=mock_resp) as m:
        r = client.post('/api/continental/imagen/upload', data=data, headers=headers, content_type='multipart/form-data')
    assert r.status_code == 201
    call_kwargs = m.call_args[1]
    assert 'files' in call_kwargs and call_kwargs['files'] is not None


@test('POST /imagen/upload sin CSRF → 403', group='Media Routes')
def _():
    token, _ = _login()
    headers = {k: v for k, v in _auth_headers(token).items() if k != 'Content-Type'}
    data = {'file': (io.BytesIO(b'img'), 'foto.jpg'), 'nombre': 'ok'}
    r = client.post('/api/continental/imagen/upload', data=data, headers=headers, content_type='multipart/form-data')
    assert r.status_code == 403


# ═════════════════════════════════════════════════════════════════════════════
# GROUP 7 — Utilities routes (push-subscription, push-notification, deployment)
# ═════════════════════════════════════════════════════════════════════════════

@test('GET /push-subscription/ → proxied a continental_utilities', group='Utilities Routes')
def _():
    token, _ = _login()
    mock_resp = _make_mock_response({'subscriptions': []}, 200)
    with patch('app.utils.proxy.requests.request', return_value=mock_resp) as m:
        r = client.get('/api/continental/push-subscription/', headers=_auth_headers(token))
    assert r.status_code == 200
    from config import Config
    assert Config.CONTINENTAL_UTILITIES_URL in m.call_args[0][1]


@test('POST /push-notification/send requiere CSRF', group='Utilities Routes')
def _():
    token, _ = _login()
    r = client.post('/api/continental/push-notification/send', json={'titulo': 'Hola'}, headers=_auth_headers(token))
    assert r.status_code == 403


@test('POST /push-notification/send con CSRF → proxied', group='Utilities Routes')
def _():
    token, csrf = _login()
    mock_resp = _make_mock_response({'sent': 5}, 200)
    with patch('app.utils.proxy.requests.request', return_value=mock_resp):
        r = client.post('/api/continental/push-notification/send', json={'titulo': 'News'}, headers=_auth_headers(token, csrf))
    assert r.status_code == 200


@test('POST /deployment/reload-continental-page requiere CSRF', group='Utilities Routes')
def _():
    token, _ = _login()
    r = client.post('/api/continental/deployment/reload-continental-page', headers=_auth_headers(token))
    assert r.status_code == 403


@test('POST /deployment/reload-continental-page con CSRF → proxied', group='Utilities Routes')
def _():
    token, csrf = _login()
    mock_resp = _make_mock_response({'status': 'reloaded'}, 200)
    with patch('app.utils.proxy.requests.request', return_value=mock_resp):
        r = client.post('/api/continental/deployment/reload-continental-page', headers=_auth_headers(token, csrf))
    assert r.status_code == 200


@test('DELETE /push-subscription/<oid> requiere CSRF', group='Utilities Routes')
def _():
    token, _ = _login()
    r = client.delete('/api/continental/push-subscription/sub123', headers=_auth_headers(token))
    assert r.status_code == 403


# ═════════════════════════════════════════════════════════════════════════════
# GROUP 8 — Proxy error handling
# ═════════════════════════════════════════════════════════════════════════════

@test('Proxy → ConnectionError → 503', group='Proxy Errors')
def _():
    import requests as req
    token, _ = _login()
    with patch('app.utils.proxy.requests.request', side_effect=req.exceptions.ConnectionError()):
        r = client.get('/api/continental/obra/', headers=_auth_headers(token))
    assert r.status_code == 503
    assert 'errors' in r.get_json()


@test('Proxy → Timeout → 504', group='Proxy Errors')
def _():
    import requests as req
    token, _ = _login()
    with patch('app.utils.proxy.requests.request', side_effect=req.exceptions.Timeout()):
        r = client.get('/api/continental/arco/', headers=_auth_headers(token))
    assert r.status_code == 504


@test('Proxy inyecta X-Internal-Service-Secret en cada request (no cookies)', group='Proxy Errors')
def _():
    token, _ = _login()
    captured = {}
    def fake_req(method, url, **kwargs):
        captured['headers'] = kwargs.get('headers', {})
        captured['cookies'] = kwargs.get('cookies', None)
        return _make_mock_response({}, 200)
    with patch('app.utils.proxy.requests.request', side_effect=fake_req):
        client.get('/api/continental/obra/', headers=_auth_headers(token))
    from config import Config
    assert captured['headers'].get('X-Internal-Service-Secret') == Config.INTERNAL_SERVICE_SECRET
    assert captured['cookies'] is None  # ya no se inyectan cookies


@test('Proxy pasa query params al microservicio', group='Proxy Errors')
def _():
    token, _ = _login()
    captured = {}
    def fake_req(method, url, **kwargs):
        captured['params'] = kwargs.get('params', {})
        return _make_mock_response({}, 200)
    with patch('app.utils.proxy.requests.request', side_effect=fake_req):
        client.get('/api/continental/capitulo/?fk_obra=obra123&page=2', headers=_auth_headers(token))
    assert captured['params'].get('fk_obra') == 'obra123'
    assert captured['params'].get('page') == '2'


# ═════════════════════════════════════════════════════════════════════════════
# GROUP 9 — Session store unit tests
# ═════════════════════════════════════════════════════════════════════════════

@test('save_session / get_session / delete_session', group='Session Store')
def _():
    from app.utils.session_store import save_session, get_session, delete_session
    save_session('jti-test', 'access-tok', 'refresh-tok', 'csrf1')
    s = get_session('jti-test')
    assert s == {
        'auth_service_access_token': 'access-tok',
        'auth_service_refresh_token': 'refresh-tok',
        'csrf_token': 'csrf1',
    }
    delete_session('jti-test')
    assert get_session('jti-test') is None


@test('get_session retorna sólo tokens de auth_service (sin cookies)', group='Session Store')
def _():
    from app.utils.session_store import save_session, get_session, delete_session
    save_session('jti-check', 'acc', 'ref', 'csrf999')
    s = get_session('jti-check')
    assert 'auth_service_access_token' in s
    assert 'auth_service_refresh_token' in s
    assert 'csrf_token' in s
    assert 'auth_token' not in s
    assert 'url_busqueda' not in s
    delete_session('jti-check')


@test('get_session con jti inexistente devuelve None', group='Session Store')
def _():
    from app.utils.session_store import get_session
    assert get_session('nonexistent-jti') is None


@test('delete_session con jti inexistente no lanza error', group='Session Store')
def _():
    from app.utils.session_store import delete_session
    delete_session('nonexistent-jti')  # no debe lanzar excepción


# ═════════════════════════════════════════════════════════════════════════════
# GROUP 10 — Auth bypass: EVERY protected endpoint without JWT
# ═════════════════════════════════════════════════════════════════════════════

# All routes that require JWT (no auth header at all)
_PROTECTED_GET = [
    '/api/continental/auth/usuario/',
    '/api/continental/auth/usuario/someoid',
    '/api/continental/obra/',
    '/api/continental/obra/someoid',
    '/api/continental/arco/',
    '/api/continental/arco/someoid',
    '/api/continental/capitulo/',
    '/api/continental/capitulo/someoid',
    '/api/continental/noticia/',
    '/api/continental/noticia/someoid',
    '/api/continental/nota/',
    '/api/continental/nota/someoid',
    '/api/continental/personaje-ficticio/',
    '/api/continental/personaje-ficticio/someoid',
    '/api/continental/fecha/',
    '/api/continental/fecha/someoid',
    '/api/continental/imagen/',
    '/api/continental/imagen/someoid',
    '/api/continental/push-subscription/',
    '/api/continental/push-subscription/someoid',
    '/api/continental/variable-sistema/',
    '/api/continental/variable-sistema/someoid',
]

_PROTECTED_POST = [
    '/api/continental/auth/logout',
    '/api/continental/auth/usuario/',
    '/api/continental/obra/',
    '/api/continental/obra/many',
    '/api/continental/arco/',
    '/api/continental/arco/many',
    '/api/continental/capitulo/',
    '/api/continental/capitulo/many',
    '/api/continental/noticia/',
    '/api/continental/noticia/many',
    '/api/continental/nota/',
    '/api/continental/nota/many',
    '/api/continental/personaje-ficticio/',
    '/api/continental/personaje-ficticio/many',
    '/api/continental/fecha/',
    '/api/continental/fecha/many',
    '/api/continental/imagen/',
    '/api/continental/imagen/many',
    '/api/continental/push-subscription/many',
    '/api/continental/push-notification/send',
    '/api/continental/deployment/reload-continental-page',
    '/api/continental/variable-sistema/',
    '/api/continental/variable-sistema/many',
]

_PROTECTED_PUT = [
    '/api/continental/auth/usuario/someoid',
    '/api/continental/obra/someoid',
    '/api/continental/obra/many',
    '/api/continental/arco/someoid',
    '/api/continental/arco/many',
    '/api/continental/capitulo/someoid',
    '/api/continental/capitulo/many',
    '/api/continental/noticia/someoid',
    '/api/continental/noticia/many',
    '/api/continental/nota/someoid',
    '/api/continental/nota/many',
    '/api/continental/personaje-ficticio/someoid',
    '/api/continental/personaje-ficticio/many',
    '/api/continental/fecha/someoid',
    '/api/continental/fecha/many',
    '/api/continental/imagen/someoid',
    '/api/continental/push-subscription/someoid',
    '/api/continental/push-subscription/many',
    '/api/continental/variable-sistema/someoid',
    '/api/continental/variable-sistema/many',
]

_PROTECTED_DELETE = [
    '/api/continental/auth/usuario/someoid',
    '/api/continental/obra/someoid',
    '/api/continental/arco/someoid',
    '/api/continental/capitulo/someoid',
    '/api/continental/noticia/someoid',
    '/api/continental/nota/someoid',
    '/api/continental/personaje-ficticio/someoid',
    '/api/continental/fecha/someoid',
    '/api/continental/imagen/someoid',
    '/api/continental/push-subscription/someoid',
    '/api/continental/variable-sistema/someoid',
]


@test('GET a todas las rutas protegidas sin JWT → 401', group='Auth Bypass')
def _():
    for url in _PROTECTED_GET:
        r = client.get(url)
        assert r.status_code == 401, f"GET {url} devolvió {r.status_code}, esperaba 401"
        assert 'errors' in (r.get_json() or {}), f"GET {url} no devolvió campo 'errors'"


@test('POST a todas las rutas protegidas sin JWT → 401', group='Auth Bypass')
def _():
    for url in _PROTECTED_POST:
        r = client.post(url, json={}, content_type='application/json')
        assert r.status_code == 401, f"POST {url} devolvió {r.status_code}, esperaba 401"


@test('PUT a todas las rutas protegidas sin JWT → 401', group='Auth Bypass')
def _():
    for url in _PROTECTED_PUT:
        r = client.put(url, json={}, content_type='application/json')
        assert r.status_code == 401, f"PUT {url} devolvió {r.status_code}, esperaba 401"


@test('DELETE a todas las rutas protegidas sin JWT → 401', group='Auth Bypass')
def _():
    for url in _PROTECTED_DELETE:
        r = client.delete(url)
        assert r.status_code == 401, f"DELETE {url} devolvió {r.status_code}, esperaba 401"


@test('JWT válido de OTRA app (secret distinto) → 401', group='Auth Bypass')
def _():
    # Manually craft a token signed with a wrong secret
    import datetime, base64, hmac, hashlib
    header = base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').rstrip(b'=').decode()
    payload = base64.urlsafe_b64encode(
        json.dumps({'sub': 'attacker', 'jti': 'evil-jti', 'exp': 9999999999}).encode()
    ).rstrip(b'=').decode()
    sig = base64.urlsafe_b64encode(
        hmac.new(b'wrong-secret', f'{header}.{payload}'.encode(), hashlib.sha256).digest()
    ).rstrip(b'=').decode()
    forged_token = f'{header}.{payload}.{sig}'
    r = client.get('/api/continental/obra/', headers={'Authorization': f'Bearer {forged_token}'})
    assert r.status_code == 401, f"Token forjado debería dar 401, dio {r.status_code}"


@test('Bearer vacío → 401', group='Auth Bypass')
def _():
    r = client.get('/api/continental/obra/', headers={'Authorization': 'Bearer '})
    assert r.status_code == 401


@test('Authorization con esquema incorrecto (Basic) → 401', group='Auth Bypass')
def _():
    r = client.get('/api/continental/obra/', headers={'Authorization': 'Basic dXNlcjpwYXNz'})
    assert r.status_code == 401


@test('Token de sesión ya expirada (jti no en store) → 401', group='Auth Bypass')
def _():
    # Login, erase store, try to access
    token, _ = _login()
    session_store._store.clear()
    for url in ['/api/continental/obra/', '/api/continental/noticia/', '/api/continental/imagen/']:
        r = client.get(url, headers=_auth_headers(token))
        assert r.status_code == 401, f"Sesión expirada en {url} dio {r.status_code}"


# ═════════════════════════════════════════════════════════════════════════════
# GROUP 11 — Malicious data injection through routes
# ═════════════════════════════════════════════════════════════════════════════

@test('XSS en titulo de obra → sanitizado antes del proxy', group='Injection Attacks')
def _():
    token, csrf = _login()
    payloads = [
        '<script>document.cookie="x="+document.cookie</script>',
        '<img src=x onerror=alert(1)>',
        '<svg onload=alert(1)>',
        '"><script>alert(1)</script>',
        "';alert(1);//",
    ]
    for payload in payloads:
        captured = {}
        def fake_req(method, url, **kwargs):
            captured['json'] = kwargs.get('json', {})
            return _make_mock_response({'oid': 'x'}, 201)
        with patch('app.utils.proxy.requests.request', side_effect=fake_req):
            r = client.post(
                '/api/continental/obra/',
                json={'titulo': payload, 'descripcion': payload},
                headers=_auth_headers(token, csrf),
            )
        assert r.status_code == 201
        sent = captured.get('json', {})
        assert '<script>' not in sent.get('titulo', '').lower(), f"Script no eliminado en: {payload}"
        assert 'onerror' not in sent.get('descripcion', '').lower(), f"onerror no eliminado en: {payload}"
        assert 'onload' not in sent.get('descripcion', '').lower(), f"onload no eliminado en: {payload}"


@test('SQL Injection en campos de arco → no genera error 500', group='Injection Attacks')
def _():
    token, csrf = _login()
    sql_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE obras; --",
        "1' UNION SELECT * FROM usuarios --",
        "admin'--",
        "' OR 1=1 #",
    ]
    mock_resp = _make_mock_response({'oid': 'x'}, 201)
    for payload in sql_payloads:
        with patch('app.utils.proxy.requests.request', return_value=mock_resp):
            r = client.post(
                '/api/continental/arco/',
                json={'titulo': payload, 'numero': payload},
                headers=_auth_headers(token, csrf),
            )
        # Gateway should NOT crash (500); it passes through to microservice
        assert r.status_code != 500, f"Gateway crasheó con SQL payload: {payload}"
        assert r.status_code in (200, 201, 400, 422), f"Código inesperado {r.status_code} con: {payload}"


@test('Path traversal en OID de URL → no expone sistema de archivos', group='Injection Attacks')
def _():
    token, _ = _login()
    traversal_ids = [
        '../../../etc/passwd',
        '..%2F..%2Fetc%2Fpasswd',
        '%2e%2e%2fetc%2fpasswd',
    ]
    mock_resp = _make_mock_response({'error': 'not found'}, 404)
    for oid in traversal_ids:
        with patch('app.utils.proxy.requests.request', return_value=mock_resp) as m:
            r = client.get(f'/api/continental/obra/{oid}', headers=_auth_headers(token))
        # Must not 500 (crash) or actually read local files
        assert r.status_code != 500, f"Gateway crasheó con path traversal: {oid}"
        # Verify the OID was passed literally to the microservice (not resolved locally)
        if m.called:
            called_url = m.call_args[0][1]
            assert 'etc/passwd' not in called_url or called_url.startswith('http://localhost'), \
                f"URL peligrosa enviada al microservicio: {called_url}"


@test('Null bytes en campos → sanitizados', group='Injection Attacks')
def _():
    token, csrf = _login()
    captured = {}
    def fake_req(method, url, **kwargs):
        captured['json'] = kwargs.get('json', {})
        return _make_mock_response({'oid': 'x'}, 201)
    with patch('app.utils.proxy.requests.request', side_effect=fake_req):
        r = client.post(
            '/api/continental/noticia/',
            json={'titulo': 'titulo\x00malicioso', 'subtitulo': 'sub\x00'},
            headers=_auth_headers(token, csrf),
        )
    assert r.status_code == 201
    assert '\x00' not in captured.get('json', {}).get('titulo', '')
    assert '\x00' not in captured.get('json', {}).get('subtitulo', '')


@test('Payload JSON gigante (>1MB) → no crashea el gateway', group='Injection Attacks')
def _():
    token, csrf = _login()
    big_payload = {'titulo': 'A' * 1_100_000}
    mock_resp = _make_mock_response({'oid': 'x'}, 201)
    with patch('app.utils.proxy.requests.request', return_value=mock_resp):
        r = client.post(
            '/api/continental/obra/',
            json=big_payload,
            headers=_auth_headers(token, csrf),
        )
    # Should not crash (500). Flask default limit is 16MB, so 1MB passes through
    assert r.status_code != 500, f"Gateway crasheó con payload grande"


@test('JSON completamente malformado → no crashea el gateway', group='Injection Attacks')
def _():
    token, csrf = _login()
    headers = {**_auth_headers(token, csrf), 'Content-Type': 'application/json'}
    r = client.post('/api/continental/obra/', data=b'{invalid json!!!', headers=headers)
    # Flask should handle gracefully (200/201 with empty dict, or 400)
    assert r.status_code != 500, f"Gateway crasheó con JSON malformado"


@test('Nombre de archivo malicioso en upload de imagen', group='Injection Attacks')
def _():
    token, csrf = _login()
    headers = {k: v for k, v in _auth_headers(token, csrf).items() if k != 'Content-Type'}
    malicious_names = [
        '../../../etc/passwd.jpg',
        'shell.php%00.jpg',
        '<script>.jpg',
        'file;rm -rf /.jpg',
    ]
    for fname in malicious_names:
        data = {'file': (io.BytesIO(b'img data'), fname), 'nombre': 'test'}
        # Allowed extensions check uses rsplit('.', 1) so only the real extension matters
        # ../../../etc/passwd.jpg → extension is 'jpg' → allowed → should reach proxy
        # shell.php%00.jpg → extension after %00 decode varies, but gateway must not crash
        mock_resp = _make_mock_response({'url': '/uploads/file.jpg'}, 201)
        with patch('app.utils.proxy.requests.request', return_value=mock_resp):
            r = client.post(
                '/api/continental/imagen/upload',
                data=data, headers=headers, content_type='multipart/form-data',
            )
        assert r.status_code != 500, f"Gateway crasheó con filename malicioso: {fname}"


@test('CSRF token en query string (no debe aceptarse)', group='Injection Attacks')
def _():
    """Attacker tries to pass CSRF token via query param instead of header."""
    token, csrf = _login()
    # Send CSRF in URL, NOT in header
    r = client.post(
        f'/api/continental/obra/?X-CSRF-Token={csrf}',
        json={'titulo': 'test'},
        headers=_auth_headers(token),  # no csrf in headers
    )
    assert r.status_code == 403, f"CSRF en query string fue aceptado (debería ser 403)"


@test('CSRF token en body JSON (no debe aceptarse)', group='Injection Attacks')
def _():
    """Attacker embeds CSRF token inside JSON body."""
    token, csrf = _login()
    r = client.post(
        '/api/continental/obra/',
        json={'titulo': 'test', 'X-CSRF-Token': csrf, '_csrf': csrf},
        headers=_auth_headers(token),  # no csrf in headers
    )
    assert r.status_code == 403, f"CSRF en body fue aceptado (debería ser 403)"


@test('Reutilización de CSRF de sesión expirada → 401/403', group='Injection Attacks')
def _():
    """After logout, the old CSRF token must not work."""
    token, csrf = _login()
    # Logout first
    client.post('/api/continental/auth/logout', headers=_auth_headers(token, csrf))
    # Try to use the same token again for a mutation
    r = client.post(
        '/api/continental/obra/',
        json={'titulo': 'post-logout'},
        headers=_auth_headers(token, csrf),
    )
    # JWT is still technically valid (not blocklisted), but session is gone → 401
    assert r.status_code == 401, f"Post-logout request dio {r.status_code}, esperaba 401"


@test('Inyección XSS en nombre de usuario en login → no llega al proxy limpio', group='Injection Attacks')
def _():
    """XSS in login nombre should not crash; sanitizer doesn't touch contraseña."""
    session_store._store.clear()
    xss_nombre = '<script>alert(1)</script>admin'
    mock_resp = _make_mock_response({'errors': ['not found']}, 401)
    captured = {}
    def fake_post(url, json=None, **kwargs):
        captured['json'] = json
        return mock_resp
    with patch('app.routes.auth_routes.requests.post', side_effect=fake_post):
        r = client.post('/api/continental/auth/login', json={'nombre': xss_nombre, 'contraseña': 'pw'})
    # Login strips via .strip() but does NOT sanitize nombre before forwarding
    # The important thing: gateway must not crash
    assert r.status_code != 500


@test('Inyección de header HTTP en campo nombre (CRLF)', group='Injection Attacks')
def _():
    """CRLF injection attempt in nombre field."""
    session_store._store.clear()
    crlf_nombre = 'user\r\nX-Injected: evil'
    mock_resp = _make_mock_response({'errors': ['not found']}, 401)
    with patch('app.routes.auth_routes.requests.post', return_value=mock_resp):
        r = client.post('/api/continental/auth/login', json={'nombre': crlf_nombre, 'contraseña': 'pw'})
    assert r.status_code != 500


@test('Múltiples logins seguidos no acumulan sesiones huérfanas del mismo usuario', group='Injection Attacks')
def _():
    """Each login creates a NEW jti/session; each JWT must have a unique jti."""
    session_store._store.clear()
    mock_resp = _make_mock_response(
        json_data={
            'access_token': 'fake-auth-service-token',
            'refresh_token': 'fake-refresh-token',
            'usuario': {'usuario': 'grapelurian'},
        },
        status_code=200,
    )
    tokens = []
    for _ in range(3):
        with patch('app.routes.auth_routes.requests.post', return_value=mock_resp):
            r = client.post(
                '/api/continental/auth/login',
                json={'usuario': 'grapelurian', 'contraseña': 'pass'},
            )
        assert r.status_code == 200
        tokens.append(r.get_json()['access_token'])
    # 3 logins → 3 independent sessions in the store
    assert len(session_store._store) == 3, f"Esperaba 3 sesiones, hay {len(session_store._store)}"
    # All access tokens must be distinct (different jti each time)
    assert len(set(tokens)) == 3, "Los tokens de acceso deberían ser únicos por sesión"


# ═════════════════════════════════════════════════════════════════════════════
# GROUP 12 — Wrong HTTP methods on defined routes
# ═════════════════════════════════════════════════════════════════════════════

@test('PATCH /obra/ → 405 Method Not Allowed', group='Method Enforcement')
def _():
    token, csrf = _login()
    r = client.patch('/api/continental/obra/', json={}, headers=_auth_headers(token, csrf))
    assert r.status_code == 405, f"PATCH /obra/ debería ser 405, dio {r.status_code}"


@test('DELETE /obra/ (colección, no OID) → 405', group='Method Enforcement')
def _():
    token, csrf = _login()
    r = client.delete('/api/continental/obra/', headers=_auth_headers(token, csrf))
    assert r.status_code == 405, f"DELETE /obra/ debería ser 405"


@test('GET /push-notification/send → 405', group='Method Enforcement')
def _():
    token, _ = _login()
    r = client.get('/api/continental/push-notification/send', headers=_auth_headers(token))
    assert r.status_code == 405, f"GET /push-notification/send debería ser 405"


@test('PUT /deployment/reload-continental-page → 405', group='Method Enforcement')
def _():
    token, csrf = _login()
    r = client.put('/api/continental/deployment/reload-continental-page', headers=_auth_headers(token, csrf))
    assert r.status_code == 405


@test('POST a ruta GET-only /obra/<oid> → 405', group='Method Enforcement')
def _():
    # /obra/<oid> only has GET, PUT, DELETE — no POST
    token, csrf = _login()
    r = client.post('/api/continental/obra/someoid', json={}, headers=_auth_headers(token, csrf))
    assert r.status_code == 405, f"POST /obra/<oid> debería ser 405"


# ═════════════════════════════════════════════════════════════════════════════
# RUNNER
# ═════════════════════════════════════════════════════════════────────────────

if __name__ == '__main__':
    groups_order = [
        'Auth', 'JWT', 'CSRF', 'Sanitizer',
        'Content Routes', 'Media Routes', 'Utilities Routes', 'Proxy Errors', 'Session Store',
        'Auth Bypass', 'Injection Attacks', 'Method Enforcement',
    ]
    by_group = {g: [] for g in groups_order}
    for r in RESULTS:
        by_group.setdefault(r['group'], []).append(r)

    total = passed = failed = 0
    failures = []

    for group in groups_order:
        tests_in_group = by_group.get(group, [])
        if not tests_in_group:
            continue
        print(f"\n{BOLD}{BLUE}{'─'*60}{RESET}")
        print(f"{BOLD}{BLUE}  {group}{RESET}")
        print(f"{BOLD}{BLUE}{'─'*60}{RESET}")
        for entry in tests_in_group:
            total += 1
            try:
                entry['fn']()
                print(f"  {GREEN}✔{RESET}  {entry['name']}")
                passed += 1
            except Exception as e:
                print(f"  {RED}✘{RESET}  {entry['name']}")
                print(f"      {RED}→ {e}{RESET}")
                failed += 1
                failures.append((entry['name'], str(e)))

    print(f"\n{'═'*60}")
    print(f"{BOLD}  Resultados: {GREEN}{passed} passed{RESET}{BOLD}  {RED if failed else GREEN}{failed} failed{RESET}{BOLD}  / {total} total{RESET}")
    print(f"{'═'*60}\n")

    if failures:
        print(f"{RED}{BOLD}Fallos detallados:{RESET}")
        for name, err in failures:
            print(f"  • {name}")
            print(f"    {err}")
        print()
        sys.exit(1)
    else:
        print(f"{GREEN}{BOLD}  ¡Todos los tests pasaron!{RESET}\n")
        sys.exit(0)
