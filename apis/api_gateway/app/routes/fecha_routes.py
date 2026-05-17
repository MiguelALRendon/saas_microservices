from flask import Blueprint, request
from app.middleware.jwt_middleware import gateway_auth_required
from app.middleware.csrf_middleware import csrf_required
from app.utils.sanitizer import sanitize_dict, sanitize_list
from app.utils.proxy import proxy_to_content
from config import Config

fecha_bp = Blueprint('fecha', __name__, url_prefix=f"{Config.API_PREFIX}/fecha")


@fecha_bp.route('/', methods=['GET'])
@gateway_auth_required
def get_fechas():
    return proxy_to_content('/fecha/')


@fecha_bp.route('/<string:oid>', methods=['GET'])
@gateway_auth_required
def get_fecha(oid):
    return proxy_to_content(f'/fecha/{oid}')


@fecha_bp.route('/', methods=['POST'])
@gateway_auth_required
@csrf_required
def create_fecha():
    data = request.get_json() or {}
    return proxy_to_content('/fecha/', sanitize_dict(data))


@fecha_bp.route('/many', methods=['POST'])
@gateway_auth_required
@csrf_required
def create_many_fechas():
    data = request.get_json() or []
    return proxy_to_content('/fecha/many', sanitize_list(data) if isinstance(data, list) else data)


@fecha_bp.route('/<string:oid>', methods=['PUT'])
@gateway_auth_required
@csrf_required
def update_fecha(oid):
    data = request.get_json() or {}
    return proxy_to_content(f'/fecha/{oid}', sanitize_dict(data))


@fecha_bp.route('/many', methods=['PUT'])
@gateway_auth_required
@csrf_required
def update_many_fechas():
    data = request.get_json() or []
    return proxy_to_content('/fecha/many', sanitize_list(data) if isinstance(data, list) else data)


@fecha_bp.route('/<string:oid>', methods=['DELETE'])
@gateway_auth_required
@csrf_required
def delete_fecha(oid):
    return proxy_to_content(f'/fecha/{oid}')
