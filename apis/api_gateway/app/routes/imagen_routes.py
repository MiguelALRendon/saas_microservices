import os
from flask import Blueprint, request, jsonify
from app.middleware.jwt_middleware import gateway_auth_required
from app.middleware.csrf_middleware import csrf_required
from app.utils.sanitizer import sanitize_dict, sanitize_list, sanitize_string
from app.utils.proxy import proxy_to_media
from config import Config

imagen_bp = Blueprint('imagen', __name__, url_prefix=f"{Config.API_PREFIX}/imagen")

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def _allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@imagen_bp.route('/', methods=['GET'])
@gateway_auth_required
def get_imagenes():
    return proxy_to_media('/imagen/')


@imagen_bp.route('/<string:oid>', methods=['GET'])
@gateway_auth_required
def get_imagen(oid):
    return proxy_to_media(f'/imagen/{oid}')


@imagen_bp.route('/upload', methods=['POST'])
@gateway_auth_required
@csrf_required
def upload_imagen():
    if 'file' not in request.files:
        return jsonify({'errors': ['No se proporcionó ningún archivo']}), 400

    file = request.files['file']
    nombre = sanitize_string(request.form.get('nombre', '').strip())

    if not nombre:
        return jsonify({'errors': ["El campo 'nombre' es requerido"]}), 400

    if not file or file.filename == '':
        return jsonify({'errors': ['Archivo no válido']}), 400

    if not _allowed_file(file.filename):
        return jsonify({'errors': ['Formato no permitido. Use: jpg, jpeg, png']}), 400

    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > MAX_FILE_SIZE:
        return jsonify({'errors': ['El archivo excede el límite de 5 MB']}), 400

    files = {'file': (file.filename, file.stream, file.content_type)}
    form_data = {'nombre': nombre}
    return proxy_to_media('/imagen/upload', files=files, form_data=form_data)


@imagen_bp.route('/', methods=['POST'])
@gateway_auth_required
@csrf_required
def create_imagen():
    data = request.get_json() or {}
    return proxy_to_media('/imagen/', sanitize_dict(data))


@imagen_bp.route('/many', methods=['POST'])
@gateway_auth_required
@csrf_required
def create_many_imagenes():
    data = request.get_json() or []
    return proxy_to_media('/imagen/many', sanitize_list(data) if isinstance(data, list) else data)


@imagen_bp.route('/<string:oid>', methods=['PUT'])
@gateway_auth_required
@csrf_required
def update_imagen(oid):
    data = request.get_json() or {}
    return proxy_to_media(f'/imagen/{oid}', sanitize_dict(data))


@imagen_bp.route('/<string:oid>', methods=['DELETE'])
@gateway_auth_required
@csrf_required
def delete_imagen(oid):
    return proxy_to_media(f'/imagen/{oid}')
