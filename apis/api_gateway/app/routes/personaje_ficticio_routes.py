from flask import Blueprint, request
from app.middleware.jwt_middleware import gateway_auth_required
from app.middleware.csrf_middleware import csrf_required
from app.utils.sanitizer import sanitize_dict, sanitize_list
from app.utils.proxy import proxy_to_content
from config import Config

personaje_ficticio_bp = Blueprint('personaje_ficticio', __name__, url_prefix=f"{Config.API_PREFIX}/personaje-ficticio")


@personaje_ficticio_bp.route('/', methods=['GET'])
@gateway_auth_required
def get_personajes():
    return proxy_to_content('/personaje-ficticio/')


@personaje_ficticio_bp.route('/<string:oid>', methods=['GET'])
@gateway_auth_required
def get_personaje(oid):
    return proxy_to_content(f'/personaje-ficticio/{oid}')


@personaje_ficticio_bp.route('/', methods=['POST'])
@gateway_auth_required
@csrf_required
def create_personaje():
    data = request.get_json() or {}
    return proxy_to_content('/personaje-ficticio/', sanitize_dict(data))


@personaje_ficticio_bp.route('/many', methods=['POST'])
@gateway_auth_required
@csrf_required
def create_many_personajes():
    data = request.get_json() or []
    return proxy_to_content('/personaje-ficticio/many', sanitize_list(data) if isinstance(data, list) else data)


@personaje_ficticio_bp.route('/<string:oid>', methods=['PUT'])
@gateway_auth_required
@csrf_required
def update_personaje(oid):
    data = request.get_json() or {}
    return proxy_to_content(f'/personaje-ficticio/{oid}', sanitize_dict(data))


@personaje_ficticio_bp.route('/many', methods=['PUT'])
@gateway_auth_required
@csrf_required
def update_many_personajes():
    data = request.get_json() or []
    return proxy_to_content('/personaje-ficticio/many', sanitize_list(data) if isinstance(data, list) else data)


@personaje_ficticio_bp.route('/<string:oid>', methods=['DELETE'])
@gateway_auth_required
@csrf_required
def delete_personaje(oid):
    return proxy_to_content(f'/personaje-ficticio/{oid}')
