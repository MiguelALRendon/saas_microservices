from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt
from app.utils.session_store import get_session


def csrf_required(f):
    """Validate X-CSRF-Token header against the stored CSRF token for this session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        jti = get_jwt().get('jti')
        session = get_session(jti)
        csrf_token = request.headers.get('X-CSRF-Token')
        if not csrf_token or not session or csrf_token != session.get('csrf_token'):
            return jsonify({'errors': ['Token CSRF inválido o ausente']}), 403
        return f(*args, **kwargs)
    return decorated
