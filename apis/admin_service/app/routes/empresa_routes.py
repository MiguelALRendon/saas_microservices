from flask import Blueprint, request
from app.utils.proxy import proxy_to_catalogues

empresa_bp = Blueprint('empresa', __name__, url_prefix='/empresa')


@empresa_bp.route('/', methods=['GET'])
def get_empresas():
    return proxy_to_catalogues('/empresa/')


@empresa_bp.route('/<string:oid>', methods=['GET'])
def get_empresa(oid):
    return proxy_to_catalogues(f'/empresa/{oid}')


@empresa_bp.route('/', methods=['POST'])
def create_empresa():
    return proxy_to_catalogues('/empresa/', request.get_json() or {})


@empresa_bp.route('/many', methods=['POST'])
def create_many_empresas():
    return proxy_to_catalogues('/empresa/many', request.get_json() or [])


@empresa_bp.route('/<string:oid>', methods=['PUT'])
def update_empresa(oid):
    return proxy_to_catalogues(f'/empresa/{oid}', request.get_json() or {})


@empresa_bp.route('/many', methods=['PUT'])
def update_many_empresas():
    return proxy_to_catalogues('/empresa/many', request.get_json() or [])


@empresa_bp.route('/<string:oid>', methods=['DELETE'])
def delete_empresa(oid):
    return proxy_to_catalogues(f'/empresa/{oid}', request.get_json() or {})


@empresa_bp.route('/list', methods=['POST'])
def get_empresa_list():
    return proxy_to_catalogues('/empresa/list', request.get_json() or {})
