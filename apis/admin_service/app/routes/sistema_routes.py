from flask import Blueprint, request
from app.utils.proxy import proxy_to_catalogues

sistema_bp = Blueprint('sistema', __name__, url_prefix='/sistema')


@sistema_bp.route('/', methods=['GET'])
def get_sistemas():
    return proxy_to_catalogues('/sistema/')


@sistema_bp.route('/<string:oid>', methods=['GET'])
def get_sistema(oid):
    return proxy_to_catalogues(f'/sistema/{oid}')


@sistema_bp.route('/', methods=['POST'])
def create_sistema():
    return proxy_to_catalogues('/sistema/', request.get_json() or {})


@sistema_bp.route('/many', methods=['POST'])
def create_many_sistemas():
    return proxy_to_catalogues('/sistema/many', request.get_json() or [])


@sistema_bp.route('/<string:oid>', methods=['PUT'])
def update_sistema(oid):
    return proxy_to_catalogues(f'/sistema/{oid}', request.get_json() or {})


@sistema_bp.route('/many', methods=['PUT'])
def update_many_sistemas():
    return proxy_to_catalogues('/sistema/many', request.get_json() or [])


@sistema_bp.route('/<string:oid>', methods=['DELETE'])
def delete_sistema(oid):
    return proxy_to_catalogues(f'/sistema/{oid}', request.get_json() or {})


@sistema_bp.route('/list', methods=['POST'])
def get_sistema_list():
    return proxy_to_catalogues('/sistema/list', request.get_json() or {})
