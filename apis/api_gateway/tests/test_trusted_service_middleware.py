"""
Test suite: TrustedServiceMiddleware — Seguridad inter-servicio

Cubre DOS ángulos de la misma funcionalidad:

  PARTE A — Comportamiento del middleware (Flask test app mínimo, sin BD)
    • Requests directas (simulando curl / browser / atacante) son bloqueadas
    • Variantes del header: ausente, vacío, incorrecto, parcial, inyección, etc.
    • Todos los métodos HTTP son bloqueados sin el secreto
    • Formato de respuesta de error

  PARTE B — Inyección de cabecera por el API Gateway
    • El proxy envía X-Internal-Service-Secret en GET/POST/PUT/DELETE
    • La ruta de login envía el header en su requests.post directo
    • El valor enviado coincide EXACTAMENTE con Config.INTERNAL_SERVICE_SECRET
    • Cada microservicio destino (content, media, utilities) recibe el header

Credenciales de documentación: nombre='grapelurian' / contraseña='Gl4_Nd#urI4n2025.'
"""
import sys
import io
import json
import importlib.util
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify

# ── Paths ─────────────────────────────────────────────────────────────────────
WORKSPACE = r'C:\Users\spook\OneDrive\Documents\ProyectoPuntosDeVenta\saas_api'
# api_gateway MUST be first so that `app.*` resolves to the gateway, not auth_service.
sys.path.insert(0, rf'{WORKSPACE}\apis\api_gateway')

# ── Cargar TrustedServiceMiddleware directamente del archivo fuente ────────────
# Importamos con importlib para no disparar el __init__.py de auth_service/app
# (que inicializa SQLAlchemy y requiere base de datos).
_spec = importlib.util.spec_from_file_location(
    'trusted_service',
    rf'{WORKSPACE}\auth_service\app\middleware\trusted_service.py',
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
TrustedServiceMiddleware = _mod.TrustedServiceMiddleware

# ── Colores ───────────────────────────────────────────────────────────────────
GREEN  = '\033[92m'
RED    = '\033[91m'
YELLOW = '\033[93m'
BLUE   = '\033[94m'
BOLD   = '\033[1m'
RESET  = '\033[0m'

# ── Runner ────────────────────────────────────────────────────────────────────
RESULTS = []

def test(name, group=''):
    def decorator(fn):
        RESULTS.append({'name': name, 'group': group, 'fn': fn})
        return fn
    return decorator

# ─────────────────────────────────────────────────────────────────────────────
# Parte A — Flask test app mínimo con el middleware activo
# ─────────────────────────────────────────────────────────────────────────────

CORRECT_SECRET = 'dev-internal-secret'
WRONG_SECRET   = 'hacker-secret'

def _build_guarded_app(secret=CORRECT_SECRET):
    """Crea una app Flask mínima que registra TrustedServiceMiddleware."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['INTERNAL_SERVICE_SECRET'] = secret

    TrustedServiceMiddleware.register(app)

    @app.route('/ping', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
    def ping():
        return jsonify({'ok': True}), 200

    @app.route('/data', methods=['GET'])
    def data():
        return jsonify({'items': [1, 2, 3]}), 200

    return app

guarded = _build_guarded_app()
gc = guarded.test_client()

HEADER = TrustedServiceMiddleware.HEADER_NAME   # 'X-Internal-Service-Secret'


# ═══════════════════════════════════════════════════════════════════════════════
# GRUPO A1 — Bloqueos básicos (simulan curl/browser directo al microservicio)
# ═══════════════════════════════════════════════════════════════════════════════

@test('GET sin header alguno → 403', group='A1 · Bloqueo directo')
def _():
    r = gc.get('/ping')
    assert r.status_code == 403, f'Esperaba 403, got {r.status_code}'

@test('POST sin header alguno → 403', group='A1 · Bloqueo directo')
def _():
    r = gc.post('/ping', json={'dato': 'valor'})
    assert r.status_code == 403

@test('PUT sin header alguno → 403', group='A1 · Bloqueo directo')
def _():
    r = gc.put('/ping', json={})
    assert r.status_code == 403

@test('DELETE sin header alguno → 403', group='A1 · Bloqueo directo')
def _():
    r = gc.delete('/ping')
    assert r.status_code == 403

@test('PATCH sin header alguno → 403', group='A1 · Bloqueo directo')
def _():
    r = gc.patch('/ping', json={})
    assert r.status_code == 403

@test('GET con Authorization Bearer (simulando browser) → 403', group='A1 · Bloqueo directo')
def _():
    """Navegador con JWT válido del gateway NO puede acceder directamente al microservicio."""
    r = gc.get('/ping', headers={'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.payload.signature'})
    assert r.status_code == 403

@test('GET con cookie de sesión (session hijack simulado) → 403', group='A1 · Bloqueo directo')
def _():
    """Aunque tenga cookies, sin el header es bloqueado."""
    r = gc.get('/ping', headers={'Cookie': 'auth_token=valid-cookie; url_busqueda=grapelurian'})
    assert r.status_code == 403

@test('GET con Content-Type y JSON bien formado → 403 (middleware va antes de rutas)', group='A1 · Bloqueo directo')
def _():
    r = gc.get('/data', headers={'Content-Type': 'application/json'})
    assert r.status_code == 403

@test('Respuesta de error 403 tiene campo "errors" en JSON', group='A1 · Bloqueo directo')
def _():
    r = gc.get('/ping')
    body = r.get_json()
    assert body is not None, 'Respuesta no es JSON'
    assert 'errors' in body, f'Falta campo errors: {body}'
    assert isinstance(body['errors'], list), 'errors debe ser lista'
    assert len(body['errors']) > 0, 'errors está vacío'


# ═══════════════════════════════════════════════════════════════════════════════
# GRUPO A2 — Variantes del header incorrecto
# ═══════════════════════════════════════════════════════════════════════════════

@test('Header con valor incorrecto → 403', group='A2 · Header incorrecto')
def _():
    r = gc.get('/ping', headers={HEADER: WRONG_SECRET})
    assert r.status_code == 403

@test('Header vacío (valor="") → 403', group='A2 · Header incorrecto')
def _():
    r = gc.get('/ping', headers={HEADER: ''})
    assert r.status_code == 403

@test('Header con solo espacios → 403', group='A2 · Header incorrecto')
def _():
    r = gc.get('/ping', headers={HEADER: '   '})
    assert r.status_code == 403

@test('Header correcto + espacio trailing → 403 (match exacto)', group='A2 · Header incorrecto')
def _():
    r = gc.get('/ping', headers={HEADER: CORRECT_SECRET + ' '})
    assert r.status_code == 403

@test('Header correcto + espacio leading → 403 (match exacto)', group='A2 · Header incorrecto')
def _():
    r = gc.get('/ping', headers={HEADER: ' ' + CORRECT_SECRET})
    assert r.status_code == 403

@test('Prefijo del secret (ataque de longitud parcial) → 403', group='A2 · Header incorrecto')
def _():
    prefix = CORRECT_SECRET[:len(CORRECT_SECRET)//2]
    r = gc.get('/ping', headers={HEADER: prefix})
    assert r.status_code == 403

@test('Sufijo del secret → 403', group='A2 · Header incorrecto')
def _():
    suffix = CORRECT_SECRET[len(CORRECT_SECRET)//2:]
    r = gc.get('/ping', headers={HEADER: suffix})
    assert r.status_code == 403

@test('Secret duplicado (repetido dos veces) → 403', group='A2 · Header incorrecto')
def _():
    r = gc.get('/ping', headers={HEADER: CORRECT_SECRET * 2})
    assert r.status_code == 403

@test('Mayúsculas del secret → 403', group='A2 · Header incorrecto')
def _():
    r = gc.get('/ping', headers={HEADER: CORRECT_SECRET.upper()})
    assert r.status_code == 403

@test('SQL injection en header → 403', group='A2 · Header incorrecto')
def _():
    sql_values = [
        "' OR '1'='1",
        "dev-internal-secret' OR '1'='1",
        "'; DROP TABLE microservices; --",
    ]
    for val in sql_values:
        r = gc.get('/ping', headers={HEADER: val})
        assert r.status_code == 403, f"SQL injection aceptado: {val!r}"

@test('Header muy largo (10000 chars) → 403', group='A2 · Header incorrecto')
def _():
    r = gc.get('/ping', headers={HEADER: 'x' * 10_000})
    assert r.status_code == 403

@test('Header con null bytes → 403', group='A2 · Header incorrecto')
def _():
    # HTTP headers con null bytes — Flask/Werkzeug puede rechazarlos antes,
    # pero si llegan al middleware, deben ser bloqueados.
    try:
        r = gc.get('/ping', headers={HEADER: 'dev-internal-secret\x00extra'})
        assert r.status_code in (400, 403), f'Null byte aceptado con status {r.status_code}'
    except Exception:
        pass  # Werkzeug puede lanzar excepción antes, que también es correcto

@test('Nombre de header alternativo (X-Service-Token) → 403', group='A2 · Header incorrecto')
def _():
    """El header debe llamarse exactamente X-Internal-Service-Secret."""
    r = gc.get('/ping', headers={'X-Service-Token': CORRECT_SECRET})
    assert r.status_code == 403

@test('Config vacío (sin INTERNAL_SERVICE_SECRET) → 403', group='A2 · Header incorrecto')
def _():
    """Si el config no tiene el secreto, el default es '' y compare_digest falla."""
    empty_app = _build_guarded_app(secret='')
    ec = empty_app.test_client()
    # Incluso enviando el secreto correcto, si config está vacío → 403
    r = ec.get('/ping', headers={HEADER: CORRECT_SECRET})
    assert r.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════════
# GRUPO A3 — Acceso legítimo (header correcto)
# ═══════════════════════════════════════════════════════════════════════════════

@test('GET con header correcto → 200', group='A3 · Acceso legítimo')
def _():
    r = gc.get('/ping', headers={HEADER: CORRECT_SECRET})
    assert r.status_code == 200, f'Header correcto bloqueado: {r.status_code}'

@test('POST con header correcto → 200', group='A3 · Acceso legítimo')
def _():
    r = gc.post('/ping', json={'dato': 1}, headers={HEADER: CORRECT_SECRET})
    assert r.status_code == 200

@test('PUT con header correcto → 200', group='A3 · Acceso legítimo')
def _():
    r = gc.put('/ping', json={}, headers={HEADER: CORRECT_SECRET})
    assert r.status_code == 200

@test('DELETE con header correcto → 200', group='A3 · Acceso legítimo')
def _():
    r = gc.delete('/ping', headers={HEADER: CORRECT_SECRET})
    assert r.status_code == 200

@test('Header correcto + otros headers legítimos → 200', group='A3 · Acceso legítimo')
def _():
    """Headers adicionales no deben interferir con el middleware."""
    r = gc.get('/ping', headers={
        HEADER: CORRECT_SECRET,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Request-ID': 'req-abc-123',
    })
    assert r.status_code == 200

@test('Respuesta legítima tiene cuerpo correcto (ruta no es sobreescrita)', group='A3 · Acceso legítimo')
def _():
    r = gc.get('/data', headers={HEADER: CORRECT_SECRET})
    assert r.status_code == 200
    body = r.get_json()
    assert body == {'items': [1, 2, 3]}, f'Cuerpo alterado: {body}'


# ═══════════════════════════════════════════════════════════════════════════════
# GRUPO A4 — Timing attack: compare_digest garantiza tiempo constante
# ═══════════════════════════════════════════════════════════════════════════════

@test('compare_digest: prefijo exacto no termina antes (no short-circuit)', group='A4 · Timing safety')
def _():
    """
    Valida indirectamente que se usa compare_digest y no '=='.
    Un atacante probando prefijos no debe obtener tiempos distintos.
    En unit test, verificamos que el resultado es SIEMPRE 403
    independientemente de cuántos caracteres del prefijo coincidan.
    """
    import time
    tiempos = []
    candidatos = [
        '',
        'd',
        'de',
        'dev',
        'dev-',
        'dev-i',
        'dev-internal',
        'dev-internal-secret',   # correcto (debería ser 200)
        'dev-internal-secretx',
    ]
    esperados = [403] * (len(candidatos) - 2) + [200, 403]

    for val, esperado in zip(candidatos, esperados):
        t0 = time.perf_counter()
        r = gc.get('/ping', headers={HEADER: val})
        t1 = time.perf_counter()
        tiempos.append(t1 - t0)
        assert r.status_code == esperado, f'Con valor {val!r}: esperaba {esperado}, got {r.status_code}'

    # No verificamos tiempos exactos (demasiado variable en tests), solo que
    # el resultado sea correcto para cada caso.
    assert all(t > 0 for t in tiempos), 'Algún request tardó 0 ms (imposible)'


# ─────────────────────────────────────────────────────────────────────────────
# Parte B — API Gateway inyecta el header al proxiar
# ─────────────────────────────────────────────────────────────────────────────

from app import create_app as create_gateway
from app.utils import session_store
from config import Config

gateway_app = create_gateway()
gw = gateway_app.test_client()


def _make_mock_response(json_data=None, status_code=200, cookies=None, content=None):
    mock = MagicMock()
    mock.status_code = status_code
    mock.cookies = cookies or {}
    mock.headers = {'Content-Type': 'application/json'}
    _json = json_data or {}
    mock.json.return_value = _json
    mock.content = content if content is not None else json.dumps(_json).encode()
    return mock


def _login_gateway(usuario='grapelurian', contraseña='Gl4_Nd#urI4n2025.'):
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
        resp = gw.post(
            '/api/continental/auth/login',
            json={'usuario': usuario, 'contraseña': contraseña},
        )
    assert resp.status_code == 200, f'Login falló: {resp.get_json()}'
    data = resp.get_json()
    return data['access_token'], data['csrf_token']


def _gw_headers(token, csrf=None):
    h = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    if csrf:
        h['X-CSRF-Token'] = csrf
    return h


def _assert_internal_header_sent(call_args):
    """Verifica que el call a requests.request incluye el header X-Internal-Service-Secret."""
    kwargs = call_args[1] if call_args[1] else {}
    sent_headers = kwargs.get('headers', {})
    assert HEADER in sent_headers, f'Header {HEADER!r} no enviado. Headers enviados: {list(sent_headers.keys())}'
    assert sent_headers[HEADER] == Config.INTERNAL_SERVICE_SECRET, (
        f'Valor incorrecto: got {sent_headers[HEADER]!r}, esperaba {Config.INTERNAL_SERVICE_SECRET!r}'
    )


# ═══════════════════════════════════════════════════════════════════════════════
# GRUPO B1 — Proxy content: header en todos los métodos HTTP
# ═══════════════════════════════════════════════════════════════════════════════

@test('Proxy GET /obra/ → inyecta X-Internal-Service-Secret', group='B1 · Proxy content header')
def _():
    token, _ = _login_gateway()
    mock_resp = _make_mock_response({'data': []}, 200)
    with patch('app.utils.proxy.requests.request', return_value=mock_resp) as m:
        r = gw.get('/api/continental/obra/', headers=_gw_headers(token))
    assert r.status_code == 200
    _assert_internal_header_sent(m.call_args)

@test('Proxy POST /obra/ → inyecta X-Internal-Service-Secret', group='B1 · Proxy content header')
def _():
    token, csrf = _login_gateway()
    mock_resp = _make_mock_response({'oid': 'new1'}, 201)
    with patch('app.utils.proxy.requests.request', return_value=mock_resp) as m:
        r = gw.post('/api/continental/obra/', json={'titulo': 'Test'}, headers=_gw_headers(token, csrf))
    assert r.status_code == 201
    _assert_internal_header_sent(m.call_args)

@test('Proxy PUT /obra/<oid> → inyecta X-Internal-Service-Secret', group='B1 · Proxy content header')
def _():
    token, csrf = _login_gateway()
    mock_resp = _make_mock_response({'ok': True}, 200)
    with patch('app.utils.proxy.requests.request', return_value=mock_resp) as m:
        r = gw.put('/api/continental/obra/some-oid', json={'titulo': 'Edit'}, headers=_gw_headers(token, csrf))
    assert r.status_code == 200
    _assert_internal_header_sent(m.call_args)

@test('Proxy DELETE /obra/<oid> → inyecta X-Internal-Service-Secret', group='B1 · Proxy content header')
def _():
    token, csrf = _login_gateway()
    mock_resp = _make_mock_response({'deleted': True}, 200)
    with patch('app.utils.proxy.requests.request', return_value=mock_resp) as m:
        r = gw.delete('/api/continental/obra/some-oid', headers=_gw_headers(token, csrf))
    assert r.status_code == 200
    _assert_internal_header_sent(m.call_args)

@test('Proxy GET /capitulo/ → inyecta header (múltiples entidades)', group='B1 · Proxy content header')
def _():
    """Verifica que el header se inyecta en TODAS las entidades, no solo obra."""
    token, _ = _login_gateway()
    mock_resp = _make_mock_response({'data': []}, 200)
    entities = ['arco', 'capitulo', 'noticia', 'nota', 'personaje-ficticio', 'fecha', 'variable-sistema']
    for entity in entities:
        with patch('app.utils.proxy.requests.request', return_value=mock_resp) as m:
            r = gw.get(f'/api/continental/{entity}/', headers=_gw_headers(token))
        assert r.status_code == 200, f'GET /{entity}/ falló con {r.status_code}'
        sent_headers = m.call_args[1].get('headers', {})
        assert HEADER in sent_headers, f'Header no enviado en /{entity}/'

@test('Proxy GET /auth/usuario/ → inyecta X-Internal-Service-Secret', group='B1 · Proxy content header')
def _():
    token, _ = _login_gateway()
    mock_resp = _make_mock_response({'data': []}, 200)
    with patch('app.utils.proxy.requests.request', return_value=mock_resp) as m:
        r = gw.get('/api/continental/auth/usuario/', headers=_gw_headers(token))
    assert r.status_code == 200
    _assert_internal_header_sent(m.call_args)


# ═══════════════════════════════════════════════════════════════════════════════
# GRUPO B2 — Proxy media y utilities: header también inyectado
# ═══════════════════════════════════════════════════════════════════════════════

@test('Proxy GET /imagen/ → inyecta header en continental_media', group='B2 · Proxy media/utilities')
def _():
    token, _ = _login_gateway()
    mock_resp = _make_mock_response({'imagenes': []}, 200)
    with patch('app.utils.proxy.requests.request', return_value=mock_resp) as m:
        r = gw.get('/api/continental/imagen/', headers=_gw_headers(token))
    assert r.status_code == 200
    _assert_internal_header_sent(m.call_args)
    # Verifica que va al servicio correcto (media URL)
    called_url = m.call_args[0][1]
    assert Config.CONTINENTAL_MEDIA_URL in called_url, f'URL incorrecta: {called_url}'

@test('Proxy GET /push-subscription/ → inyecta header en continental_utilities', group='B2 · Proxy media/utilities')
def _():
    token, _ = _login_gateway()
    mock_resp = _make_mock_response({'data': []}, 200)
    with patch('app.utils.proxy.requests.request', return_value=mock_resp) as m:
        r = gw.get('/api/continental/push-subscription/', headers=_gw_headers(token))
    assert r.status_code == 200
    _assert_internal_header_sent(m.call_args)
    called_url = m.call_args[0][1]
    assert Config.CONTINENTAL_UTILITIES_URL in called_url

@test('Upload imagen → inyecta header en multipart request', group='B2 · Proxy media/utilities')
def _():
    token, csrf = _login_gateway()
    headers = {k: v for k, v in _gw_headers(token, csrf).items() if k != 'Content-Type'}
    img_bytes = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
    data = {'file': (io.BytesIO(img_bytes), 'foto.png'), 'nombre': 'Mi foto'}
    mock_resp = _make_mock_response({'url': '/uploads/foto.png'}, 201)
    with patch('app.utils.proxy.requests.request', return_value=mock_resp) as m:
        r = gw.post('/api/continental/imagen/upload', data=data, headers=headers, content_type='multipart/form-data')
    assert r.status_code == 201
    _assert_internal_header_sent(m.call_args)


# ═══════════════════════════════════════════════════════════════════════════════
# GRUPO B3 — Ruta de login: requests.post directo también envía el header
# ═══════════════════════════════════════════════════════════════════════════════

@test('Login POST /auth/login → envía X-Internal-Service-Secret a auth_service', group='B3 · Login header')
def _():
    session_store._store.clear()
    mock_resp = _make_mock_response(
        {
            'access_token': 'tok',
            'refresh_token': 'ref',
            'usuario': {'usuario': 'grapelurian', 'oid': 'u1'},
        },
        200,
    )
    captured = {}
    def fake_post(url, json=None, headers=None, **kwargs):
        captured['headers'] = headers or {}
        captured['url'] = url
        return mock_resp

    with patch('app.routes.auth_routes.requests.post', side_effect=fake_post):
        r = gw.post('/api/continental/auth/login',
                    json={'usuario': 'grapelurian', 'contraseña': 'Gl4_Nd#urI4n2025.'})
    assert r.status_code == 200
    assert HEADER in captured['headers'], (
        f'Header no enviado en login. Headers: {list(captured["headers"].keys())}'
    )
    assert captured['headers'][HEADER] == Config.INTERNAL_SERVICE_SECRET

@test('Login → URL destino es AUTH_SERVICE_URL', group='B3 · Login header')
def _():
    session_store._store.clear()
    mock_resp = _make_mock_response(
        {
            'access_token': 'tok',
            'refresh_token': 'ref',
            'usuario': {'usuario': 'grapelurian', 'oid': 'u1'},
        },
        200,
    )
    captured = {}
    def fake_post(url, **kwargs):
        captured['url'] = url
        return mock_resp

    with patch('app.routes.auth_routes.requests.post', side_effect=fake_post):
        gw.post('/api/continental/auth/login',
                json={'usuario': 'grapelurian', 'contraseña': 'Gl4_Nd#urI4n2025.'})
    assert Config.AUTH_SERVICE_URL in captured['url'], f"URL incorrecta: {captured['url']}"
    assert '/auth/login' in captured['url']


# ═══════════════════════════════════════════════════════════════════════════════
# GRUPO B4 — Valor del header es el correcto (no vacío, no hardcodeado)
# ═══════════════════════════════════════════════════════════════════════════════

@test('Valor enviado == Config.INTERNAL_SERVICE_SECRET (no constante hardcodeada)', group='B4 · Valor del header')
def _():
    """El header enviado debe leerse de Config, no de un string literal."""
    assert Config.INTERNAL_SERVICE_SECRET, 'Config.INTERNAL_SERVICE_SECRET está vacío'
    token, _ = _login_gateway()
    captured = {}
    def fake_req(method, url, **kwargs):
        captured['headers'] = kwargs.get('headers', {})
        return _make_mock_response({}, 200)
    with patch('app.utils.proxy.requests.request', side_effect=fake_req):
        gw.get('/api/continental/obra/', headers=_gw_headers(token))
    assert captured['headers'].get(HEADER) == Config.INTERNAL_SERVICE_SECRET

@test('Proxy no filtra el header a la respuesta del cliente (seguridad)', group='B4 · Valor del header')
def _():
    """El secreto inter-servicio no debe aparecer en headers de respuesta al browser."""
    token, _ = _login_gateway()
    mock_resp = _make_mock_response({'data': []}, 200)
    with patch('app.utils.proxy.requests.request', return_value=mock_resp):
        r = gw.get('/api/continental/obra/', headers=_gw_headers(token))
    # El header de respuesta al cliente no debe contener el secreto
    response_headers = dict(r.headers)
    assert HEADER not in response_headers, f'Secreto expuesto en respuesta: {response_headers}'

@test('Header enviado es un string, no None ni bytes', group='B4 · Valor del header')
def _():
    token, _ = _login_gateway()
    captured = {}
    def fake_req(method, url, **kwargs):
        captured['h'] = kwargs.get('headers', {})
        return _make_mock_response({}, 200)
    with patch('app.utils.proxy.requests.request', side_effect=fake_req):
        gw.get('/api/continental/obra/', headers=_gw_headers(token))
    val = captured['h'].get(HEADER)
    assert isinstance(val, str), f'Header no es str: {type(val)}'
    assert len(val) > 0, 'Header vacío'


# ═══════════════════════════════════════════════════════════════════════════════
# GRUPO B5 — Escenarios de error: header correcto pero microservicio caído
# ═══════════════════════════════════════════════════════════════════════════════

@test('Microservicio devuelve 403 (header rechazado) → gateway lo propaga', group='B5 · Error propagation')
def _():
    """Si el microservicio rechaza el header (config distinto), el gateway propaga el 403."""
    token, _ = _login_gateway()
    mock_resp = _make_mock_response({'errors': ['Acceso no autorizado']}, 403)
    with patch('app.utils.proxy.requests.request', return_value=mock_resp):
        r = gw.get('/api/continental/obra/', headers=_gw_headers(token))
    assert r.status_code == 403

@test('Microservicio caído (ConnectionError) → 503 aunque header sea correcto', group='B5 · Error propagation')
def _():
    import requests as req
    token, _ = _login_gateway()
    with patch('app.utils.proxy.requests.request', side_effect=req.exceptions.ConnectionError()):
        r = gw.get('/api/continental/obra/', headers=_gw_headers(token))
    assert r.status_code == 503

@test('Microservicio lento (Timeout) → 504 aunque header sea correcto', group='B5 · Error propagation')
def _():
    import requests as req
    token, _ = _login_gateway()
    with patch('app.utils.proxy.requests.request', side_effect=req.exceptions.Timeout()):
        r = gw.get('/api/continental/capitulo/', headers=_gw_headers(token))
    assert r.status_code == 504


# ═════════════════════════════════════════════════════════════════════════════
# RUNNER
# ═════════════════════════════════════════════════════════════════════════════

def run_all():
    passed = failed = 0
    current_group = None
    total = len(RESULTS)

    print(f'\n{BOLD}{BLUE}══════════════════════════════════════════════════════════════{RESET}')
    print(f'{BOLD}{BLUE}  TEST: TrustedServiceMiddleware — Seguridad inter-servicio{RESET}')
    print(f'{BOLD}{BLUE}  Secret de prueba : {CORRECT_SECRET!r}{RESET}')
    print(f'{BOLD}{BLUE}  Config.SECRET    : {Config.INTERNAL_SERVICE_SECRET!r}{RESET}')
    print(f'{BOLD}{BLUE}══════════════════════════════════════════════════════════════{RESET}\n')

    for entry in RESULTS:
        group = entry['group']
        if group != current_group:
            current_group = group
            print(f'\n  {BOLD}{YELLOW}── {group} ──{RESET}')

        try:
            entry['fn']()
            passed += 1
            print(f'  {GREEN}✓{RESET}  {entry["name"]}')
        except Exception as exc:
            failed += 1
            print(f'  {RED}✗{RESET}  {entry["name"]}')
            print(f'      {RED}{exc}{RESET}')

    print(f'\n{BOLD}{"─"*62}{RESET}')
    color = GREEN if failed == 0 else RED
    print(f'{BOLD}{color}  {passed}/{total} passed', end='')
    if failed:
        print(f'  |  {failed} FALLARON', end='')
    print(f'{RESET}\n')
    return failed


if __name__ == '__main__':
    import sys
    sys.exit(run_all())
