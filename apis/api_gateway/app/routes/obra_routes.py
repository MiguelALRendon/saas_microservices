from flask import Blueprint, request
from app.middleware.jwt_middleware import gateway_auth_required
from app.middleware.csrf_middleware import csrf_required
from app.utils.sanitizer import sanitize_dict, sanitize_list
from app.utils.proxy import proxy_to_content
from config import Config

obra_bp = Blueprint('obra', __name__, url_prefix=f"{Config.API_PREFIX}/obra")


@obra_bp.route('/', methods=['GET'])
@gateway_auth_required
def get_obras():
    return proxy_to_content('/obra/')


@obra_bp.route('/<string:oid>', methods=['GET'])
@gateway_auth_required
def get_obra(oid):
    return proxy_to_content(f'/obra/{oid}')


@obra_bp.route('/', methods=['POST'])
@gateway_auth_required
@csrf_required
def create_obra():
    data = request.get_json() or {}
    return proxy_to_content('/obra/', sanitize_dict(data))


@obra_bp.route('/many', methods=['POST'])
@gateway_auth_required
@csrf_required
def create_many_obras():
    data = request.get_json() or []
    return proxy_to_content('/obra/many', sanitize_list(data) if isinstance(data, list) else data)


@obra_bp.route('/<string:oid>', methods=['PUT'])
@gateway_auth_required
@csrf_required
def update_obra(oid):
    data = request.get_json() or {}
    return proxy_to_content(f'/obra/{oid}', sanitize_dict(data))


@obra_bp.route('/many', methods=['PUT'])
@gateway_auth_required
@csrf_required
def update_many_obras():
    data = request.get_json() or []
    return proxy_to_content('/obra/many', sanitize_list(data) if isinstance(data, list) else data)


@obra_bp.route('/<string:oid>', methods=['DELETE'])
@gateway_auth_required
@csrf_required
def delete_obra(oid):
    return proxy_to_content(f'/obra/{oid}')
