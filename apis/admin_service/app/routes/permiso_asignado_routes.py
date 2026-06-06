from flask import Blueprint, request
from app.utils.proxy import proxy_to_auth

# Admin expone `/permiso-asignado` (con guión) y traduce al backend `/permiso_asignado`
permiso_asignado_bp = Blueprint('permiso_asignado', __name__, url_prefix='/permiso-asignado')

_BACKEND_PATH = '/permiso_asignado'


@permiso_asignado_bp.route('/', methods=['GET'])
def get_list():
    return proxy_to_auth(f'{_BACKEND_PATH}/')


@permiso_asignado_bp.route('/<string:oid>', methods=['GET'])
def get_one(oid):
    return proxy_to_auth(f'{_BACKEND_PATH}/{oid}')


@permiso_asignado_bp.route('/', methods=['POST'])
def create_one():
    return proxy_to_auth(f'{_BACKEND_PATH}/', request.get_json() or {})


@permiso_asignado_bp.route('/many', methods=['POST'])
def create_many():
    return proxy_to_auth(f'{_BACKEND_PATH}/many', request.get_json() or [])


@permiso_asignado_bp.route('/<string:oid>', methods=['PUT'])
def update_one(oid):
    return proxy_to_auth(f'{_BACKEND_PATH}/{oid}', request.get_json() or {})


@permiso_asignado_bp.route('/many', methods=['PUT'])
def update_many():
    return proxy_to_auth(f'{_BACKEND_PATH}/many', request.get_json() or [])


@permiso_asignado_bp.route('/<string:oid>', methods=['DELETE'])
def delete_one(oid):
    return proxy_to_auth(f'{_BACKEND_PATH}/{oid}', request.get_json() or {})


@permiso_asignado_bp.route('/list', methods=['POST'])
def get_by_oid_list():
    return proxy_to_auth(f'{_BACKEND_PATH}/list', request.get_json() or {})
