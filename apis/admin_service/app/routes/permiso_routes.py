from flask import Blueprint, request
from app.utils.proxy import proxy_to_auth

permiso_bp = Blueprint('permiso', __name__, url_prefix='/permiso')


@permiso_bp.route('/', methods=['GET'])
def get_permisos():
    return proxy_to_auth('/permiso/')


@permiso_bp.route('/<string:oid>', methods=['GET'])
def get_permiso(oid):
    return proxy_to_auth(f'/permiso/{oid}')


@permiso_bp.route('/', methods=['POST'])
def create_permiso():
    return proxy_to_auth('/permiso/', request.get_json() or {})


@permiso_bp.route('/many', methods=['POST'])
def create_many_permisos():
    return proxy_to_auth('/permiso/many', request.get_json() or [])


@permiso_bp.route('/<string:oid>', methods=['PUT'])
def update_permiso(oid):
    return proxy_to_auth(f'/permiso/{oid}', request.get_json() or {})


@permiso_bp.route('/many', methods=['PUT'])
def update_many_permisos():
    return proxy_to_auth('/permiso/many', request.get_json() or [])


@permiso_bp.route('/<string:oid>', methods=['DELETE'])
def delete_permiso(oid):
    return proxy_to_auth(f'/permiso/{oid}', request.get_json() or {})


@permiso_bp.route('/list', methods=['POST'])
def get_permiso_list():
    return proxy_to_auth('/permiso/list', request.get_json() or {})
