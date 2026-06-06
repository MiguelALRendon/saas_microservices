from flask import Blueprint, request
from app.utils.proxy import proxy_to_branch

empleado_bp = Blueprint('empleado', __name__, url_prefix='/empleado')


@empleado_bp.route('/', methods=['GET'])
def get_empleados():
    return proxy_to_branch('/empleado/')


@empleado_bp.route('/<string:oid>', methods=['GET'])
def get_empleado(oid):
    return proxy_to_branch(f'/empleado/{oid}')


@empleado_bp.route('/', methods=['POST'])
def create_empleado():
    return proxy_to_branch('/empleado/', request.get_json() or {})


@empleado_bp.route('/many', methods=['POST'])
def create_many_empleados():
    return proxy_to_branch('/empleado/many', request.get_json() or [])


@empleado_bp.route('/<string:oid>', methods=['PUT'])
def update_empleado(oid):
    return proxy_to_branch(f'/empleado/{oid}', request.get_json() or {})


@empleado_bp.route('/many', methods=['PUT'])
def update_many_empleados():
    return proxy_to_branch('/empleado/many', request.get_json() or [])


@empleado_bp.route('/<string:oid>', methods=['DELETE'])
def delete_empleado(oid):
    return proxy_to_branch(f'/empleado/{oid}', request.get_json() or {})


@empleado_bp.route('/list', methods=['POST'])
def get_empleado_list():
    return proxy_to_branch('/empleado/list', request.get_json() or {})
