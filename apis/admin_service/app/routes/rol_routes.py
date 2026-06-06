from flask import Blueprint, request
from app.utils.proxy import proxy_to_auth

rol_bp = Blueprint('rol', __name__, url_prefix='/rol')


@rol_bp.route('/', methods=['GET'])
def get_roles():
    return proxy_to_auth('/rol/')


@rol_bp.route('/<string:oid>', methods=['GET'])
def get_rol(oid):
    return proxy_to_auth(f'/rol/{oid}')


@rol_bp.route('/', methods=['POST'])
def create_rol():
    return proxy_to_auth('/rol/', request.get_json() or {})


@rol_bp.route('/many', methods=['POST'])
def create_many_roles():
    return proxy_to_auth('/rol/many', request.get_json() or [])


@rol_bp.route('/<string:oid>', methods=['PUT'])
def update_rol(oid):
    return proxy_to_auth(f'/rol/{oid}', request.get_json() or {})


@rol_bp.route('/many', methods=['PUT'])
def update_many_roles():
    return proxy_to_auth('/rol/many', request.get_json() or [])


@rol_bp.route('/<string:oid>', methods=['DELETE'])
def delete_rol(oid):
    return proxy_to_auth(f'/rol/{oid}', request.get_json() or {})


@rol_bp.route('/list', methods=['POST'])
def get_rol_list():
    return proxy_to_auth('/rol/list', request.get_json() or {})
