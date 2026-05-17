from flask import Blueprint, request
from app.middleware.jwt_middleware import gateway_auth_required
from app.middleware.csrf_middleware import csrf_required
from app.utils.sanitizer import sanitize_dict, sanitize_list
from app.utils.proxy import proxy_to_content
from config import Config

variable_sistema_bp = Blueprint('variable_sistema', __name__, url_prefix=f"{Config.API_PREFIX}/variable-sistema")


@variable_sistema_bp.route('/', methods=['GET'])
@gateway_auth_required
def get_variables():
    return proxy_to_content('/variable-sistema/')


@variable_sistema_bp.route('/<string:oid>', methods=['GET'])
@gateway_auth_required
def get_variable(oid):
    return proxy_to_content(f'/variable-sistema/{oid}')


@variable_sistema_bp.route('/', methods=['POST'])
@gateway_auth_required
@csrf_required
def create_variable():
    data = request.get_json() or {}
    return proxy_to_content('/variable-sistema/', sanitize_dict(data))


@variable_sistema_bp.route('/many', methods=['POST'])
@gateway_auth_required
@csrf_required
def create_many_variables():
    data = request.get_json() or []
    return proxy_to_content('/variable-sistema/many', sanitize_list(data) if isinstance(data, list) else data)


@variable_sistema_bp.route('/<string:oid>', methods=['PUT'])
@gateway_auth_required
@csrf_required
def update_variable(oid):
    data = request.get_json() or {}
    return proxy_to_content(f'/variable-sistema/{oid}', sanitize_dict(data))


@variable_sistema_bp.route('/many', methods=['PUT'])
@gateway_auth_required
@csrf_required
def update_many_variables():
    data = request.get_json() or []
    return proxy_to_content('/variable-sistema/many', sanitize_list(data) if isinstance(data, list) else data)


@variable_sistema_bp.route('/<string:oid>', methods=['DELETE'])
@gateway_auth_required
@csrf_required
def delete_variable(oid):
    return proxy_to_content(f'/variable-sistema/{oid}')
