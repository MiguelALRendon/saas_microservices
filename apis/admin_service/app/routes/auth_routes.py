import requests
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt
from config import Config
from app.middleware.jwt_middleware import gateway_auth_required
from app.middleware.csrf_middleware import csrf_required
from app.utils.session_store import store
from galurensoft_api_kit.bff import close_session, open_session

auth_bp = Blueprint('auth', __name__, url_prefix=f"{Config.API_PREFIX}/auth")


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({'errors': ['No se proporcionaron datos']}), 400

    usuario = (data.get('usuario') or '').strip()
    contraseña = data.get('contraseña', '')
    if not usuario or not contraseña:
        return jsonify({'errors': ['usuario y contraseña son requeridos']}), 400

    try:
        resp = requests.post(
            f"{Config.AUTH_SERVICE_URL}/auth/login",
            json={'usuario': usuario, 'contraseña': contraseña},
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
    access = auth_data.get('access_token')
    if not access:
        return jsonify({'errors': ['Error interno: no se obtuvo token de autenticación']}), 500

    result = open_session(
        store,
        identity=usuario,
        upstream={
            'auth_service_access_token': access,
            'auth_service_refresh_token': auth_data.get('refresh_token') or '',
        },
    )
    return jsonify({
        'access_token': result['access_token'],
        'csrf_token': result['csrf_token'],
        'usuario': auth_data.get('usuario', {}),
        'roles': auth_data.get('roles', []),
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@gateway_auth_required
@csrf_required
def logout():
    close_session(store, get_jwt().get('jti'))
    return jsonify({'message': 'Sesión cerrada exitosamente'}), 200
