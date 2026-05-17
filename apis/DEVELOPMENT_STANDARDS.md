# Estándares de Desarrollo — APIs Intermedias (Gateways)

Este documento define los estándares de estructura, seguridad, configuración y convenciones para crear APIs intermedias (gateways) que conecten clientes frontend con microservicios internos.

---

## 📁 Estructura de Proyecto

```
{gateway_name}/
├── app/
│   ├── __init__.py                  # Factory de aplicación Flask
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── jwt_middleware.py        # Decorador @gateway_auth_required
│   │   └── csrf_middleware.py       # Decorador @csrf_required
│   ├── routes/
│   │   ├── __init__.py              # register_blueprints(app)
│   │   ├── auth_routes.py           # Login, logout, CRUD de usuario
│   │   └── {entity}_routes.py      # Una ruta por entidad/recurso
│   └── utils/
│       ├── __init__.py
│       ├── session_store.py         # Store de sesión en memoria (o Redis en prod)
│       ├── sanitizer.py             # Sanitización de inputs
│       └── proxy.py                 # Funciones de proxy a microservicios
├── tests/
│   └── test_gateway.py             # Tests de integración con Flask test client
├── config.py                        # Configuración centralizada
├── run.py                           # Punto de entrada
├── requirements.txt
├── .env
└── .env.example
```

---

## ⚙️ Configuración (config.py)

```python
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Seguridad
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'dev-jwt-secret-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get('JWT_EXPIRES_HOURS', 1)))

    # Servidor
    HOST = os.environ.get('HOST') or '0.0.0.0'
    PORT = int(os.environ.get('PORT') or 8200)
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')

    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS') or 'http://localhost:5173,http://localhost:3000'

    # URLs de microservicios destino
    SERVICE_A_URL = os.environ.get('SERVICE_A_URL') or 'http://localhost:8101'
    SERVICE_B_URL = os.environ.get('SERVICE_B_URL') or 'http://localhost:8102'
```

**Reglas:**
- Siempre proveer valor por defecto seguro para desarrollo
- Secrets de producción solo vía variables de entorno del servidor, nunca hardcodeados
- `DEBUG = False` en producción
- Una variable de URL por cada microservicio destino

---

## 🔌 Variables de Entorno (.env.example)

```bash
# Seguridad
SECRET_KEY=dev-secret-change-in-production
JWT_SECRET_KEY=dev-jwt-secret-change-in-production
JWT_EXPIRES_HOURS=1

# Servidor
HOST=0.0.0.0
PORT=8200
DEBUG=True

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Microservicios destino
SERVICE_A_URL=http://localhost:8101
SERVICE_B_URL=http://localhost:8102
```

---

## 🏭 Factory de Aplicación (app/__init__.py)

```python
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    jwt.init_app(app)
    CORS(
        app,
        resources={r'/api/*': {'origins': Config.CORS_ORIGINS.split(',')}},
        supports_credentials=True,
    )

    from app.routes import register_blueprints
    register_blueprints(app)

    return app
```

**Reglas:**
- CORS restringido solo al prefijo `/api/*`
- `supports_credentials=True` obligatorio (el frontend envía el JWT en cada request)
- Blueprints registrados mediante `register_blueprints` en `app/routes/__init__.py`
- No importar blueprints directamente en el factory; delegar a `register_blueprints`

---

## 🗂️ Registro de Blueprints (app/routes/__init__.py)

```python
def register_blueprints(app):
    from app.routes.auth_routes import auth_bp
    from app.routes.entity_a_routes import entity_a_bp
    from app.routes.entity_b_routes import entity_b_bp

    for bp in [auth_bp, entity_a_bp, entity_b_bp]:
        app.register_blueprint(bp)
```

**Reglas:**
- Importar blueprints dentro de la función (evita imports circulares)
- Un blueprint por archivo de rutas
- Registrar todos mediante un bucle `for`

---

## 🔐 Sesión y Autenticación

### Flujo completo

```
Frontend → POST /api/.../auth/login
  → Gateway llama al microservicio de auth
  → Extrae las credenciales de sesión del microservicio (cookies, token, etc.)
  → Genera su propio JWT + CSRF token
  → Guarda {jti → credenciales_microservicio + csrf_token} en session store
  → Devuelve access_token + csrf_token al frontend

Frontend → GET /api/.../recurso/
  Authorization: Bearer <access_token>
  → Gateway valida JWT + verifica jti en session store
  → Inyecta credenciales del microservicio en la request proxied

Frontend → POST/PUT/DELETE /api/.../recurso/
  Authorization: Bearer <access_token>
  X-CSRF-Token: <csrf_token>
  → Gateway valida JWT + jti + CSRF header
  → Inyecta credenciales + proxied al microservicio
```

### Session Store (app/utils/session_store.py)

Almacena las credenciales del microservicio indexadas por el `jti` (JWT ID) del token del gateway.

```python
# In-memory — reemplazar con Redis en producción
_store: dict = {}

def save_session(jti: str, credencial_1: str, credencial_2: str, csrf_token: str) -> None:
    _store[jti] = {
        'credencial_1': credencial_1,
        'credencial_2': credencial_2,
        'csrf_token': csrf_token,
    }

def get_session(jti: str) -> dict | None:
    return _store.get(jti)

def delete_session(jti: str) -> None:
    _store.pop(jti, None)

def get_microservice_credentials(jti: str) -> dict | None:
    session = _store.get(jti)
    if not session:
        return None
    # Devolver solo las credenciales que se inyectan al microservicio
    # (excluir csrf_token del dict de credenciales)
    return {
        'credencial_1': session['credencial_1'],
        'credencial_2': session['credencial_2'],
    }
```

**Reglas:**
- El `csrf_token` nunca se incluye en las credenciales inyectadas al microservicio
- En desarrollo: dict en memoria (se pierde al reiniciar)
- En producción: Redis con TTL igual al `JWT_ACCESS_TOKEN_EXPIRES`

---

## 🔑 Middleware de Autenticación (app/middleware/jwt_middleware.py)

```python
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from app.utils.session_store import get_session

def gateway_auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({'errors': ['Token inválido o expirado']}), 401

        jti = get_jwt().get('jti')
        if not get_session(jti):
            return jsonify({'errors': ['Sesión expirada o no encontrada']}), 401

        return f(*args, **kwargs)
    return decorated
```

**Reglas:**
- Verifica TANTO la firma del JWT como la existencia del `jti` en el session store
- Firma válida + `jti` no encontrado = sesión ya expirada o logout manual → 401
- Nunca devolver `{"error": "..."}` en singular — siempre `{"errors": ["..."]}`

---

## 🛡️ Middleware CSRF (app/middleware/csrf_middleware.py)

```python
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt
from app.utils.session_store import get_session

def csrf_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        jti = get_jwt().get('jti')
        session = get_session(jti)
        csrf_token = request.headers.get('X-CSRF-Token')
        if not csrf_token or not session or csrf_token != session.get('csrf_token'):
            return jsonify({'errors': ['Token CSRF inválido o ausente']}), 403
        return f(*args, **kwargs)
    return decorated
```

**Reglas:**
- El CSRF token se valida **solo desde el header `X-CSRF-Token`**
- CSRF en query string o en body JSON no se acepta bajo ninguna circunstancia
- Este decorador se aplica después de `@gateway_auth_required` (el JWT ya fue validado)

---

## 📍 Estructura de Rutas

### Orden de decoradores

```python
# Correcto — gateway_auth_required va primero (outer), csrf_required va segundo (inner)
@entity_bp.route('/', methods=['POST'])
@gateway_auth_required   # Se ejecuta primero: valida JWT
@csrf_required           # Se ejecuta segundo: valida CSRF
def create_entity():
    ...
```

### Plantilla estándar de rutas por entidad

```python
from flask import Blueprint, request
from app.middleware.jwt_middleware import gateway_auth_required
from app.middleware.csrf_middleware import csrf_required
from app.utils.sanitizer import sanitize_dict, sanitize_list
from app.utils.proxy import proxy_to_service_a

entity_bp = Blueprint('entity', __name__, url_prefix='/api/{sistema}/entity')


# ── Lecturas (solo JWT) ───────────────────────────────────────────────────────

@entity_bp.route('/', methods=['GET'])
@gateway_auth_required
def get_list():
    return proxy_to_service_a('/entity/')


@entity_bp.route('/<string:oid>', methods=['GET'])
@gateway_auth_required
def get_one(oid):
    return proxy_to_service_a(f'/entity/{oid}')


# ── Mutaciones (JWT + CSRF) ───────────────────────────────────────────────────

@entity_bp.route('/', methods=['POST'])
@gateway_auth_required
@csrf_required
def create():
    data = request.get_json() or {}
    return proxy_to_service_a('/entity/', sanitize_dict(data))


@entity_bp.route('/many', methods=['POST'])
@gateway_auth_required
@csrf_required
def create_many():
    data = request.get_json() or []
    return proxy_to_service_a('/entity/many', sanitize_list(data) if isinstance(data, list) else data)


@entity_bp.route('/<string:oid>', methods=['PUT'])
@gateway_auth_required
@csrf_required
def update(oid):
    data = request.get_json() or {}
    return proxy_to_service_a(f'/entity/{oid}', sanitize_dict(data))


@entity_bp.route('/many', methods=['PUT'])
@gateway_auth_required
@csrf_required
def update_many():
    data = request.get_json() or []
    return proxy_to_service_a('/entity/many', sanitize_list(data) if isinstance(data, list) else data)


@entity_bp.route('/<string:oid>', methods=['DELETE'])
@gateway_auth_required
@csrf_required
def delete(oid):
    return proxy_to_service_a(f'/entity/{oid}')
```

**Reglas de rutas:**
- GET: solo `@gateway_auth_required`
- POST, PUT, DELETE: `@gateway_auth_required` + `@csrf_required`
- Datos de entrada en mutaciones: pasar por `sanitize_dict` o `sanitize_list` antes del proxy
- Siempre usar `request.get_json() or {}` / `or []` para evitar `None`
- El prefijo de URL sigue el patrón `/api/{nombre_sistema}/{entidad}`

### Rutas de autenticación (auth_routes.py)

```python
@auth_bp.route('/login', methods=['POST'])
def login():
    # force=True + silent=True: acepta cualquier Content-Type, nunca lanza 415
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({'errors': ['No se proporcionaron datos']}), 400

    # 1. Validar campos requeridos
    # 2. Llamar al microservicio de auth con requests.post(timeout=10)
    # 3. Si falla conexión → 503; si microservicio rechaza → propagar su status
    # 4. Extraer credenciales de la respuesta del microservicio
    # 5. Si no hay credenciales → 500
    # 6. Generar csrf_token = secrets.token_hex(32)
    # 7. Crear JWT: access_token = create_access_token(identity=nombre)
    # 8. Extraer jti: decoded = decode_token(access_token); jti = decoded['jti']
    # 9. save_session(jti, credencial_1, credencial_2, csrf_token)
    # 10. Devolver access_token + csrf_token + datos_usuario
    ...

@auth_bp.route('/logout', methods=['POST'])
@gateway_auth_required
@csrf_required
def logout():
    jti = get_jwt().get('jti')
    delete_session(jti)
    return jsonify({'message': 'Sesión cerrada exitosamente'}), 200
```

---

## 🔀 Proxy (app/utils/proxy.py)

```python
import requests
from flask import request, jsonify, Response
from flask_jwt_extended import get_jwt
from app.utils.session_store import get_microservice_credentials
from config import Config


def _proxy(base_url: str, path: str, json_data=None, files=None, form_data=None):
    jti = get_jwt().get('jti')
    credentials = get_microservice_credentials(jti)
    if credentials is None:
        return jsonify({'errors': ['Sesión inválida o expirada']}), 401

    url = f'{base_url}{path}'
    kwargs = {
        'cookies': credentials,   # o 'headers': ..., dependiendo del microservicio
        'params': request.args.to_dict(),   # reenvía query params
        'timeout': 30,
    }

    if files:
        kwargs['files'] = files
        if form_data:
            kwargs['data'] = form_data
    elif json_data is not None:
        kwargs['json'] = json_data

    try:
        resp = requests.request(request.method, url, **kwargs)
        return Response(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get('Content-Type', 'application/json'),
        )
    except requests.exceptions.ConnectionError:
        return jsonify({'errors': ['Microservicio no disponible']}), 503
    except requests.exceptions.Timeout:
        return jsonify({'errors': ['El microservicio tardó demasiado en responder']}), 504
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


# Una función de acceso por microservicio destino
def proxy_to_service_a(path: str, json_data=None):
    return _proxy(Config.SERVICE_A_URL, path, json_data=json_data)

def proxy_to_service_b(path: str, json_data=None, files=None, form_data=None):
    return _proxy(Config.SERVICE_B_URL, path, json_data=json_data, files=files, form_data=form_data)
```

**Reglas:**
- Un wrapper `proxy_to_*` por cada microservicio destino
- Siempre reenviar `request.args.to_dict()` como `params` (respeta los query params del cliente)
- `timeout=30` en el proxy general; `timeout=10` en el login
- Errores de red: 503 (ConnectionError) y 504 (Timeout)
- La respuesta del microservicio se reenvía verbatim al cliente (status + content_type preservados)

---

## 🧹 Sanitizador (app/utils/sanitizer.py)

```python
import re

_SCRIPT_RE = re.compile(r'<\s*script[^>]*>.*?<\s*/\s*script\s*>', re.IGNORECASE | re.DOTALL)
_DANGEROUS_TAGS_RE = re.compile(
    r'<\s*(iframe|object|embed|form|input|button|meta|link|base)\b[^>]*>.*?<\s*/\s*\1\s*>',
    re.IGNORECASE | re.DOTALL,
)
_EVENT_HANDLERS_RE = re.compile(r'\bon\w+\s*=', re.IGNORECASE)

# Campos que NO se sanitizan: contraseñas y rich text con HTML legítimo
_SKIP_KEYS = {'contraseña', 'password', 'texto_*', 'descripcion_larga'}


def sanitize_string(value: str) -> str:
    if not isinstance(value, str):
        return value
    value = _SCRIPT_RE.sub('', value)
    value = _DANGEROUS_TAGS_RE.sub('', value)
    value = _EVENT_HANDLERS_RE.sub('', value)
    value = value.replace('\x00', '')
    return value


def sanitize_dict(data: dict) -> dict:
    # Recursivo: aplica a dicts anidados y listas
    ...

def sanitize_list(data: list) -> list:
    # Aplica sanitize_dict/sanitize_string a cada elemento
    ...
```

**Reglas:**
- Llamar `sanitize_dict` en todos los bodies de mutaciones (POST/PUT) antes del proxy
- Llamar `sanitize_list` cuando el body es un array (rutas `/many`)
- Definir explícitamente qué claves se excluyen de la sanitización (`_SKIP_KEYS`)
- Excluir siempre contraseñas y campos de rich text/HTML que el admin escriba intencionalmente
- Nunca sanitizar en GET (no hay body de entrada)

---

## 📁 Uploads de Archivos

Cuando una ruta acepta `multipart/form-data`:

```python
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

def _allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@entity_bp.route('/upload', methods=['POST'])
@gateway_auth_required
@csrf_required
def upload():
    if 'file' not in request.files:
        return jsonify({'errors': ['No se proporcionó ningún archivo']}), 400

    file = request.files['file']
    nombre = sanitize_string(request.form.get('nombre', '').strip())

    if not nombre:
        return jsonify({'errors': ["El campo 'nombre' es requerido"]}), 400
    if not file or file.filename == '':
        return jsonify({'errors': ['Archivo no válido']}), 400
    if not _allowed_file(file.filename):
        return jsonify({'errors': ['Formato no permitido']}), 400

    # Verificar tamaño sin cargar todo en memoria
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > MAX_FILE_SIZE:
        return jsonify({'errors': ['El archivo excede el límite permitido']}), 400

    files = {'file': (file.filename, file.stream, file.content_type)}
    form_data = {'nombre': nombre}
    return proxy_to_service_b('/entity/upload', files=files, form_data=form_data)
```

**Reglas:**
- Validar extensión, presencia de archivo y tamaño **antes** de llamar al proxy
- Sanitizar con `sanitize_string` todos los campos de formulario de texto
- Nunca confiar en el `content_type` del archivo — validar siempre por extensión
- El gateway no procesa ni almacena el archivo; solo lo valida y reenvía

---

## 📖 Respuestas Estándar

El gateway es transparente: devuelve la respuesta del microservicio tal cual.  
Las respuestas propias del gateway (errores de auth, CSRF, validación) siguen este formato:

### Error de autenticación (401)
```json
{ "errors": ["Token inválido o expirado"] }
```

### Error CSRF (403)
```json
{ "errors": ["Token CSRF inválido o ausente"] }
```

### Error de validación (400)
```json
{ "errors": ["nombre y contraseña son requeridos"] }
```

### Error de microservicio no disponible (503)
```json
{ "errors": ["Microservicio no disponible"] }
```

### Error de timeout (504)
```json
{ "errors": ["El microservicio tardó demasiado en responder"] }
```

### Login exitoso (200)
```json
{
  "access_token": "eyJ...",
  "csrf_token": "a3f9...",
  "usuario": { ...datos del microservicio... }
}
```

**Regla invariable:** Toda respuesta de error del gateway usa `{"errors": ["mensaje"]}` como array, nunca `{"error": "mensaje"}` en singular.

---

## 📦 Dependencias (requirements.txt)

```txt
flask
flask-jwt-extended
flask-cors
requests
python-dotenv
```

---

## 🧪 Tests

Los tests usan el Flask test client con `unittest.mock.patch` para simular microservicios.  
**No se requieren microservicios corriendo para ejecutar los tests.**

### Estructura mínima del test

```python
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, r'ruta/al/gateway')
from app import create_app
from app.utils import session_store

app = create_app()
client = app.test_client()

def _make_mock_response(json_data=None, status_code=200, cookies=None):
    mock = MagicMock()
    mock.status_code = status_code
    mock.cookies = cookies or {}
    mock.headers = {'Content-Type': 'application/json'}
    mock.json.return_value = json_data or {}
    mock.content = json.dumps(json_data or {}).encode()
    return mock
```

### Cobertura obligatoria

| Área | Qué verificar |
|---|---|
| Auth | Login válido, login sin datos, login con credenciales rechazadas por el microservicio, logout, logout sin JWT, logout con CSRF incorrecto |
| JWT Middleware | Sin token → 401, token inválido → 401, jti no en store → 401 |
| CSRF Middleware | Sin header → 403, header incorrecto → 403, CSRF en query string → 403, CSRF en body → 403 |
| Auth bypass | Todas las rutas GET sin JWT → 401, todas las POST/PUT/DELETE sin JWT → 401 |
| Sanitizer | Scripts eliminados, event handlers eliminados, null bytes eliminados, campos excluidos no modificados |
| Proxy | Cookies inyectadas, query params reenviados, ConnectionError → 503, Timeout → 504 |
| Uploads | Sin archivo → 400, sin nombre → 400, extensión inválida → 400, >MAX_SIZE → 400 |
| Métodos HTTP | Métodos no declarados → 405 |
| Inyección | XSS en campos, CSRF reutilizado post-logout → 401 |

---

## ✅ Checklist de Implementación

### Estructura
- [ ] Carpetas `app/middleware/`, `app/routes/`, `app/utils/` creadas con sus `__init__.py`
- [ ] `config.py`, `run.py`, `requirements.txt`, `.env.example` presentes

### Seguridad
- [ ] `@gateway_auth_required` en todas las rutas (excepto login)
- [ ] `@csrf_required` en todas las rutas POST, PUT y DELETE (excepto login)
- [ ] `sanitize_dict` / `sanitize_list` aplicado en todos los bodies de mutación
- [ ] Uploads validan extensión y tamaño antes del proxy
- [ ] `get_json(force=True, silent=True)` en el endpoint de login (evita 415)
- [ ] CSRF generado con `secrets.token_hex(32)` (64 caracteres hex)
- [ ] Session store usa `jti` del JWT (no `sub`, no `identity`)
- [ ] `csrf_token` excluido de las credenciales inyectadas al microservicio
- [ ] `DEBUG=False` en `.env.example`

### Proxy
- [ ] Un wrapper `proxy_to_*` por microservicio destino
- [ ] `timeout=30` en proxy general, `timeout=10` en login
- [ ] Query params reenviados con `request.args.to_dict()`
- [ ] Errores de red → 503/504 (no 500)

### Respuestas
- [ ] Todos los errores del gateway usan `{"errors": ["..."]}` (array)
- [ ] Login devuelve `access_token`, `csrf_token` y datos del usuario

### Tests
- [ ] `tests/test_gateway.py` con cobertura de las áreas listadas arriba
- [ ] Tests corren sin microservicios corriendo (todo mockeado)
- [ ] 0 fallos antes de hacer merge

---

## 🚧 Limitaciones de Desarrollo vs. Producción

| Aspecto | Desarrollo | Producción |
|---|---|---|
| Session store | Dict en memoria | Redis con TTL |
| JWT blocklist (logout) | No existe | Redis blocklist |
| Rate limiting | No existe | Flask-Limiter en `/auth/login` |
| HTTPS | No | Nginx + certificado |
| Secrets | `.env` local | Variables del servidor / vault |
| Workers | 1 proceso Flask | Gunicorn multi-worker |
| `DEBUG` | `True` | `False` |
