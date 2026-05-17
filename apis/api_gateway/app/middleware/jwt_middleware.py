from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from app.utils.session_store import get_session


def gateway_auth_required(f):
    """Validate Bearer JWT and verify that an active gateway session exists."""
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
