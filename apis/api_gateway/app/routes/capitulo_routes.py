from flask import Blueprint, request
from app.middleware.jwt_middleware import gateway_auth_required
from app.middleware.csrf_middleware import csrf_required
from app.utils.sanitizer import sanitize_dict, sanitize_list
from app.utils.proxy import proxy_to_content
from config import Config

capitulo_bp = Blueprint('capitulo', __name__, url_prefix=f"{Config.API_PREFIX}/capitulo")


@capitulo_bp.route('/', methods=['GET'])
@gateway_auth_required
def get_capitulos():
    return proxy_to_content('/capitulo/')


@capitulo_bp.route('/<string:oid>', methods=['GET'])
@gateway_auth_required
def get_capitulo(oid):
    return proxy_to_content(f'/capitulo/{oid}')


@capitulo_bp.route('/', methods=['POST'])
@gateway_auth_required
@csrf_required
def create_capitulo():
    data = request.get_json() or {}
    return proxy_to_content('/capitulo/', sanitize_dict(data))


@capitulo_bp.route('/many', methods=['POST'])
@gateway_auth_required
@csrf_required
def create_many_capitulos():
    data = request.get_json() or []
    return proxy_to_content('/capitulo/many', sanitize_list(data) if isinstance(data, list) else data)


@capitulo_bp.route('/<string:oid>', methods=['PUT'])
@gateway_auth_required
@csrf_required
def update_capitulo(oid):
    data = request.get_json() or {}
    return proxy_to_content(f'/capitulo/{oid}', sanitize_dict(data))


@capitulo_bp.route('/many', methods=['PUT'])
@gateway_auth_required
@csrf_required
def update_many_capitulos():
    data = request.get_json() or []
    return proxy_to_content('/capitulo/many', sanitize_list(data) if isinstance(data, list) else data)


@capitulo_bp.route('/<string:oid>', methods=['DELETE'])
@gateway_auth_required
@csrf_required
def delete_capitulo(oid):
    return proxy_to_content(f'/capitulo/{oid}')
