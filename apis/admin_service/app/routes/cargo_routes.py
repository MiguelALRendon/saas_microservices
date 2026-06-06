from flask import Blueprint, request
from app.utils.proxy import proxy_to_branch

cargo_bp = Blueprint('cargo', __name__, url_prefix='/cargo')


@cargo_bp.route('/', methods=['GET'])
def get_cargos():
    return proxy_to_branch('/cargo/')


@cargo_bp.route('/<string:oid>', methods=['GET'])
def get_cargo(oid):
    return proxy_to_branch(f'/cargo/{oid}')


@cargo_bp.route('/', methods=['POST'])
def create_cargo():
    return proxy_to_branch('/cargo/', request.get_json() or {})


@cargo_bp.route('/many', methods=['POST'])
def create_many_cargos():
    return proxy_to_branch('/cargo/many', request.get_json() or [])


@cargo_bp.route('/<string:oid>', methods=['PUT'])
def update_cargo(oid):
    return proxy_to_branch(f'/cargo/{oid}', request.get_json() or {})


@cargo_bp.route('/many', methods=['PUT'])
def update_many_cargos():
    return proxy_to_branch('/cargo/many', request.get_json() or [])


@cargo_bp.route('/<string:oid>', methods=['DELETE'])
def delete_cargo(oid):
    return proxy_to_branch(f'/cargo/{oid}', request.get_json() or {})


@cargo_bp.route('/list', methods=['POST'])
def get_cargo_list():
    return proxy_to_branch('/cargo/list', request.get_json() or {})
