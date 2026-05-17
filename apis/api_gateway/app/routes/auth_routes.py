import secrets
import requests
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt, decode_token
from app.middleware.jwt_middleware import gateway_auth_required
from app.middleware.csrf_middleware import csrf_required
from app.utils.sanitizer import sanitize_dict
from app.utils.session_store import save_session, delete_session
from app.utils.proxy import proxy_to_auth
from config import Config

auth_bp = Blueprint('auth', __name__, url_prefix=f"{Config.API_PREFIX}/auth")


@auth_bp.route('/login', methods=['POST'])
def login():
    # silent=True + force=True: accept any Content-Type and return None on parse failure
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({'errors': ['No se proporcionaron datos']}), 400

    usuario_str = (data.get('usuario') or '').strip()
    contraseña = data.get('contraseña', '')

    if not usuario_str or not contraseña:
        return jsonify({'errors': ['usuario y contraseña son requeridos']}), 400

    try:
        resp = requests.post(
            f"{Config.AUTH_SERVICE_URL}/auth/login",
            json={'usuario': usuario_str, 'contraseña': contraseña},
            headers={'X-Internal-Service-Secret': Config.INTERNAL_SERVICE_SECRET},
            timeout=10,
        )
    except requests.exceptions.ConnectionError:
        return jsonify({'errors': ['Servicio de autenticación no disponible']}), 503
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500

    if resp.status_code != 200:
        try:
            return jsonify(resp.json()), resp.status_code
        except Exception:
            return jsonify({'errors': ['Error de autenticación']}), resp.status_code

    auth_data = resp.json()
    auth_service_access_token = auth_data.get('access_token')
    auth_service_refresh_token = auth_data.get('refresh_token')

    if not auth_service_access_token:
        return jsonify({'errors': ['Error interno: no se obtuvo token de autenticación']}), 500

    csrf_token = secrets.token_hex(32)
    access_token = create_access_token(identity=usuario_str)
    decoded = decode_token(access_token)
    jti = decoded['jti']

    save_session(jti, auth_service_access_token, auth_service_refresh_token or '', csrf_token)

    try:
        usuario_data = auth_data.get('usuario', {})
    except Exception:
        usuario_data = {}

    return jsonify({
        'access_token': access_token,
        'csrf_token': csrf_token,
        'usuario': usuario_data,
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@gateway_auth_required
@csrf_required
def logout():
    jti = get_jwt().get('jti')
    delete_session(jti)
    return jsonify({'message': 'Sesión cerrada exitosamente'}), 200


# ── CRUD Usuario ──────────────────────────────────────────────────────────────

@auth_bp.route('/usuario/', methods=['GET'])
@gateway_auth_required
def get_usuarios():
    return proxy_to_auth('/auth/usuario/')


@auth_bp.route('/usuario/<string:oid>', methods=['GET'])
@gateway_auth_required
def get_usuario(oid):
    return proxy_to_auth(f'/auth/usuario/{oid}')


@auth_bp.route('/usuario/', methods=['POST'])
@gateway_auth_required
@csrf_required
def create_usuario():
    data = request.get_json() or {}
    return proxy_to_auth('/auth/usuario/', sanitize_dict(data))


@auth_bp.route('/usuario/<string:oid>', methods=['PUT'])
@gateway_auth_required
@csrf_required
def update_usuario(oid):
    data = request.get_json() or {}
    return proxy_to_auth(f'/auth/usuario/{oid}', sanitize_dict(data))


@auth_bp.route('/usuario/<string:oid>', methods=['DELETE'])
@gateway_auth_required
@csrf_required
def delete_usuario(oid):
    return proxy_to_auth(f'/auth/usuario/{oid}')


@auth_bp.route('/usuario/list', methods=['POST'])
@gateway_auth_required
def get_usuario_list():
    data = request.get_json() or {}
    return proxy_to_auth('/auth/usuario/list', data)
