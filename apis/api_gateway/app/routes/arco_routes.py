from flask import Blueprint, request
from app.middleware.jwt_middleware import gateway_auth_required
from app.middleware.csrf_middleware import csrf_required
from app.utils.sanitizer import sanitize_dict, sanitize_list
from app.utils.proxy import proxy_to_content
from config import Config

arco_bp = Blueprint('arco', __name__, url_prefix=f"{Config.API_PREFIX}/arco")


@arco_bp.route('/', methods=['GET'])
@gateway_auth_required
def get_arcos():
    return proxy_to_content('/arco/')


@arco_bp.route('/<string:oid>', methods=['GET'])
@gateway_auth_required
def get_arco(oid):
    return proxy_to_content(f'/arco/{oid}')


@arco_bp.route('/', methods=['POST'])
@gateway_auth_required
@csrf_required
def create_arco():
    data = request.get_json() or {}
    return proxy_to_content('/arco/', sanitize_dict(data))


@arco_bp.route('/many', methods=['POST'])
@gateway_auth_required
@csrf_required
def create_many_arcos():
    data = request.get_json() or []
    return proxy_to_content('/arco/many', sanitize_list(data) if isinstance(data, list) else data)


@arco_bp.route('/<string:oid>', methods=['PUT'])
@gateway_auth_required
@csrf_required
def update_arco(oid):
    data = request.get_json() or {}
    return proxy_to_content(f'/arco/{oid}', sanitize_dict(data))


@arco_bp.route('/many', methods=['PUT'])
@gateway_auth_required
@csrf_required
def update_many_arcos():
    data = request.get_json() or []
    return proxy_to_content('/arco/many', sanitize_list(data) if isinstance(data, list) else data)


@arco_bp.route('/<string:oid>', methods=['DELETE'])
@gateway_auth_required
@csrf_required
def delete_arco(oid):
    return proxy_to_content(f'/arco/{oid}')
