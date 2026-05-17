import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from app import db
from app.models.imagen import Imagen
from app.schemas.imagen_schema import ImagenSchema
from app.utils import ImageProcessor, generate_unique_url_busqueda

imagen_bp = Blueprint('imagen', __name__, url_prefix='/imagen')


@imagen_bp.route('/uploads/<path:filename>', methods=['GET'])
def serve_upload(filename):
    """Sirve archivos subidos en modo desarrollo."""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_folder, filename)


@imagen_bp.route('/upload', methods=['POST'])
def upload_imagen():
    try:
        if 'file' not in request.files:
            return jsonify({'errors': ['No se proporcionó ningún archivo']}), 400

        file = request.files['file']
        nombre = request.form.get('nombre', '').strip()

        if not nombre:
            return jsonify({'errors': ["El campo 'nombre' es requerido"]}), 400

        if not file or file.filename == '':
            return jsonify({'errors': ['Archivo no válido']}), 400

        if not ImageProcessor.validar_extension(file.filename):
            return jsonify({'errors': ['Formato no permitido. Use: jpg, jpeg, png']}), 400

        # Verificar tamaño antes de guardar
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > ImageProcessor.MAX_SIZE:
            return jsonify({'errors': ['El archivo excede el límite de 5 MB']}), 400

        nombre_sanitizado = ImageProcessor.sanitizar_nombre(nombre)
        extension = ImageProcessor.obtener_extension(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']

        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        nombre_archivo = ImageProcessor.generar_nombre_unico(nombre_sanitizado, extension, upload_folder)
        ruta_archivo = os.path.join(upload_folder, nombre_archivo)
        file.save(ruta_archivo)

        try:
            ImageProcessor.optimizar_imagen(ruta_archivo)

            url_busqueda = generate_unique_url_busqueda(nombre_sanitizado, Imagen)

            if current_app.config.get('DEBUG'):
                base_url = current_app.config['BASE_URL']
                url_archivo = f"{base_url}/imagen/uploads/{nombre_archivo}"
            else:
                url_archivo = f"https://images.galurian.com/{nombre_archivo}"

            imagen = Imagen(
                nombre=nombre,
                url_archivo=url_archivo,
                url_busqueda=url_busqueda,
                estatus=1,
            )
            db.session.add(imagen)
            db.session.commit()
            return jsonify(ImagenSchema.serialize(imagen)), 201

        except Exception as e:
            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)
            db.session.rollback()
            return jsonify({'errors': [str(e)]}), 500

    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@imagen_bp.route('/<string:oid>', methods=['GET'])
def get_imagen(oid):
    try:
        imagen = Imagen.query.filter(Imagen.id == oid, Imagen.estatus == 1).first()
        if not imagen:
            return jsonify({'errors': ['Imagen no encontrada']}), 404
        return jsonify(ImagenSchema.serialize(imagen)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@imagen_bp.route('/', methods=['GET'])
def get_imagenes():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        nombre = request.args.get('nombre', type=str)

        query = Imagen.query.filter(Imagen.estatus == 1).order_by(Imagen.created_at.desc())
        if nombre:
            query = query.filter(Imagen.nombre.ilike(f'%{nombre}%'))

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'data': ImagenSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@imagen_bp.route('/', methods=['POST'])
def create_imagen():
    """Registra una imagen manualmente (sin subir archivo)."""
    try:
        data = request.get_json()
        errors = ImagenSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 400

        if not data.get('url_archivo'):
            return jsonify({'errors': ['url_archivo es requerido']}), 400

        url_busqueda = data.get('url_busqueda') or generate_unique_url_busqueda(data['nombre'], Imagen)
        imagen = Imagen(
            nombre=data['nombre'],
            url_archivo=data['url_archivo'],
            url_busqueda=url_busqueda,
            estatus=1,
        )
        db.session.add(imagen)
        db.session.commit()
        return jsonify(ImagenSchema.serialize(imagen)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@imagen_bp.route('/many', methods=['POST'])
def create_many_imagenes():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de imágenes']}), 400

        created, errors = [], []
        for idx, item in enumerate(data):
            validation_errors = ImagenSchema.validate_create(item)
            if not item.get('url_archivo'):
                validation_errors.append('url_archivo es requerido')
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            url_busqueda = item.get('url_busqueda') or generate_unique_url_busqueda(item['nombre'], Imagen)
            imagen = Imagen(
                nombre=item['nombre'],
                url_archivo=item['url_archivo'],
                url_busqueda=url_busqueda,
                estatus=1,
            )
            db.session.add(imagen)
            created.append(imagen)

        if created:
            db.session.commit()
        response = {'created': len(created), 'data': ImagenSchema.serialize_list(created)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@imagen_bp.route('/<string:oid>', methods=['PUT'])
def update_imagen(oid):
    try:
        imagen = Imagen.query.filter(Imagen.id == oid, Imagen.estatus == 1).first()
        if not imagen:
            return jsonify({'errors': ['Imagen no encontrada']}), 404

        data = request.get_json()
        for field in ['nombre', 'url_archivo', 'url_busqueda']:
            if field in data:
                setattr(imagen, field, data[field])

        imagen.updated_at = datetime.now()
        db.session.commit()
        return jsonify(ImagenSchema.serialize(imagen)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@imagen_bp.route('/many', methods=['PUT'])
def update_many_imagenes():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de imágenes']}), 400

        updated, errors = [], []
        for idx, item in enumerate(data):
            if 'id' not in item:
                errors.append({'index': idx, 'errors': ['id es requerido']})
                continue
            imagen = Imagen.query.filter(Imagen.id == item['id'], Imagen.estatus == 1).first()
            if not imagen:
                errors.append({'index': idx, 'errors': ['Imagen no encontrada']})
                continue
            for field in ['nombre', 'url_archivo', 'url_busqueda']:
                if field in item:
                    setattr(imagen, field, item[field])
            imagen.updated_at = datetime.now()
            updated.append(imagen)

        if updated:
            db.session.commit()
        response = {'updated': len(updated), 'data': ImagenSchema.serialize_list(updated)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@imagen_bp.route('/<string:oid>', methods=['DELETE'])
def delete_imagen(oid):
    """Soft delete + elimina el archivo físico si existe en UPLOAD_FOLDER."""
    try:
        imagen = Imagen.query.filter(Imagen.id == oid, Imagen.estatus == 1).first()
        if not imagen:
            return jsonify({'errors': ['Imagen no encontrada']}), 404

        upload_folder = current_app.config['UPLOAD_FOLDER']
        nombre_archivo = os.path.basename(imagen.url_archivo)
        ruta_archivo = os.path.join(upload_folder, nombre_archivo)
        if os.path.exists(ruta_archivo):
            try:
                os.remove(ruta_archivo)
            except Exception:
                pass

        imagen.estatus = -1
        imagen.updated_at = datetime.now()
        db.session.commit()
        return jsonify({'message': 'Imagen eliminada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@imagen_bp.route('/list', methods=['POST'])
def get_imagen_list():
    try:
        data = request.get_json()
        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400
        oid_list = data.get('oid_list', [])
        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400
        imagenes = Imagen.query.filter(Imagen.id.in_(oid_list), Imagen.estatus == 1).all()
        return jsonify(ImagenSchema.serialize_list(imagenes)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
