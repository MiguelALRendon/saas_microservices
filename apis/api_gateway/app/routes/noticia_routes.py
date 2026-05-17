from flask import Blueprint, request
from app.middleware.jwt_middleware import gateway_auth_required
from app.middleware.csrf_middleware import csrf_required
from app.utils.sanitizer import sanitize_dict, sanitize_list
from app.utils.proxy import proxy_to_content
from config import Config

noticia_bp = Blueprint('noticia', __name__, url_prefix=f"{Config.API_PREFIX}/noticia")


@noticia_bp.route('/', methods=['GET'])
@gateway_auth_required
def get_noticias():
    return proxy_to_content('/noticia/')


@noticia_bp.route('/<string:oid>', methods=['GET'])
@gateway_auth_required
def get_noticia(oid):
    return proxy_to_content(f'/noticia/{oid}')


@noticia_bp.route('/', methods=['POST'])
@gateway_auth_required
@csrf_required
def create_noticia():
    data = request.get_json() or {}
    return proxy_to_content('/noticia/', sanitize_dict(data))


@noticia_bp.route('/many', methods=['POST'])
@gateway_auth_required
@csrf_required
def create_many_noticias():
    data = request.get_json() or []
    return proxy_to_content('/noticia/many', sanitize_list(data) if isinstance(data, list) else data)


@noticia_bp.route('/<string:oid>', methods=['PUT'])
@gateway_auth_required
@csrf_required
def update_noticia(oid):
    data = request.get_json() or {}
    return proxy_to_content(f'/noticia/{oid}', sanitize_dict(data))


@noticia_bp.route('/many', methods=['PUT'])
@gateway_auth_required
@csrf_required
def update_many_noticias():
    data = request.get_json() or []
    return proxy_to_content('/noticia/many', sanitize_list(data) if isinstance(data, list) else data)


@noticia_bp.route('/<string:oid>', methods=['DELETE'])
@gateway_auth_required
@csrf_required
def delete_noticia(oid):
    return proxy_to_content(f'/noticia/{oid}')
