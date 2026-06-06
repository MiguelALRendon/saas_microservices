from flask import Blueprint, request
from app.utils.proxy import proxy_to_catalogues

sucursal_bp = Blueprint('sucursal', __name__, url_prefix='/sucursal')


@sucursal_bp.route('/', methods=['GET'])
def get_sucursales():
    return proxy_to_catalogues('/sucursal/')


@sucursal_bp.route('/<string:oid>', methods=['GET'])
def get_sucursal(oid):
    return proxy_to_catalogues(f'/sucursal/{oid}')


@sucursal_bp.route('/', methods=['POST'])
def create_sucursal():
    return proxy_to_catalogues('/sucursal/', request.get_json() or {})


@sucursal_bp.route('/many', methods=['POST'])
def create_many_sucursales():
    return proxy_to_catalogues('/sucursal/many', request.get_json() or [])


@sucursal_bp.route('/<string:oid>', methods=['PUT'])
def update_sucursal(oid):
    return proxy_to_catalogues(f'/sucursal/{oid}', request.get_json() or {})


@sucursal_bp.route('/many', methods=['PUT'])
def update_many_sucursales():
    return proxy_to_catalogues('/sucursal/many', request.get_json() or [])


@sucursal_bp.route('/<string:oid>', methods=['DELETE'])
def delete_sucursal(oid):
    return proxy_to_catalogues(f'/sucursal/{oid}', request.get_json() or {})


@sucursal_bp.route('/list', methods=['POST'])
def get_sucursal_list():
    return proxy_to_catalogues('/sucursal/list', request.get_json() or {})
