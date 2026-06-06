from flask import Blueprint, request
from app.utils.proxy import proxy_to_auth

usuario_bp = Blueprint('usuario', __name__, url_prefix='/usuario')


@usuario_bp.route('/', methods=['GET'])
def get_usuarios():
    return proxy_to_auth('/usuario/')


@usuario_bp.route('/<string:oid>', methods=['GET'])
def get_usuario(oid):
    return proxy_to_auth(f'/usuario/{oid}')


@usuario_bp.route('/', methods=['POST'])
def create_usuario():
    return proxy_to_auth('/usuario/', request.get_json() or {})


@usuario_bp.route('/many', methods=['POST'])
def create_many_usuarios():
    return proxy_to_auth('/usuario/many', request.get_json() or [])


@usuario_bp.route('/<string:oid>', methods=['PUT'])
def update_usuario(oid):
    return proxy_to_auth(f'/usuario/{oid}', request.get_json() or {})


@usuario_bp.route('/many', methods=['PUT'])
def update_many_usuarios():
    return proxy_to_auth('/usuario/many', request.get_json() or [])


@usuario_bp.route('/<string:oid>', methods=['DELETE'])
def delete_usuario(oid):
    return proxy_to_auth(f'/usuario/{oid}', request.get_json() or {})


@usuario_bp.route('/list', methods=['POST'])
def get_usuario_list():
    return proxy_to_auth('/usuario/list', request.get_json() or {})
