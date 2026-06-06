from flask import Blueprint, request
from app.utils.proxy import proxy_to_branch

empleado_sucursal_bp = Blueprint('empleado_sucursal', __name__, url_prefix='/empleado-sucursal')


@empleado_sucursal_bp.route('/', methods=['GET'])
def get_list():
    return proxy_to_branch('/empleado-sucursal/')


@empleado_sucursal_bp.route('/<string:oid>', methods=['GET'])
def get_one(oid):
    return proxy_to_branch(f'/empleado-sucursal/{oid}')


@empleado_sucursal_bp.route('/', methods=['POST'])
def create_one():
    return proxy_to_branch('/empleado-sucursal/', request.get_json() or {})


@empleado_sucursal_bp.route('/many', methods=['POST'])
def create_many():
    return proxy_to_branch('/empleado-sucursal/many', request.get_json() or [])


@empleado_sucursal_bp.route('/<string:oid>', methods=['PUT'])
def update_one(oid):
    return proxy_to_branch(f'/empleado-sucursal/{oid}', request.get_json() or {})


@empleado_sucursal_bp.route('/many', methods=['PUT'])
def update_many():
    return proxy_to_branch('/empleado-sucursal/many', request.get_json() or [])


@empleado_sucursal_bp.route('/<string:oid>', methods=['DELETE'])
def delete_one(oid):
    return proxy_to_branch(f'/empleado-sucursal/{oid}', request.get_json() or {})


@empleado_sucursal_bp.route('/list', methods=['POST'])
def get_by_oid_list():
    return proxy_to_branch('/empleado-sucursal/list', request.get_json() or {})
