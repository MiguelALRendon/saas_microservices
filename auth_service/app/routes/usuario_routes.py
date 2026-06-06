from flask import Blueprint, request, jsonify
from app import db
from app.models.usuario import Usuario
from app.schemas.usuario_schema import UsuarioSchema
from app.enums import BaseObjectEstatus
from app.utils import hash_password
from datetime import datetime

usuario_bp = Blueprint('usuario', __name__, url_prefix='/usuario')


@usuario_bp.route('/<string:oid>', methods=['GET'])
def get_usuario(oid):
    """Obtiene un usuario por su OID (detalle con junctions resueltas)."""
    try:
        usuario = Usuario.query.filter(
            Usuario.oid == oid,
            Usuario.estatus != BaseObjectEstatus.ELIMINADO
        ).first()

        if not usuario:
            return jsonify({'errors': ['Usuario no encontrado']}), 404

        per_page = request.args.get('embedded_per_page', 25, type=int)
        return jsonify(UsuarioSchema.serialize_detail(usuario, per_page=per_page)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@usuario_bp.route('/', methods=['GET'])
def get_usuarios():
    """Listado de usuarios con paginación y filtros."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        usuario_filter = request.args.get('usuario', type=str)
        fk_sistema = request.args.get('fkSistema', type=str)

        query = Usuario.query.filter(Usuario.estatus != BaseObjectEstatus.ELIMINADO)
        if usuario_filter:
            query = query.filter(Usuario.usuario.ilike(f'%{usuario_filter}%'))
        if fk_sistema:
            query = query.filter(Usuario.fkSistema == fk_sistema)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'data': UsuarioSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@usuario_bp.route('/', methods=['POST'])
def create_usuario():
    """Crea un nuevo usuario."""
    try:
        data = request.get_json()

        errors = UsuarioSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 422

        if Usuario.query.filter_by(usuario=data['usuario']).first():
            return jsonify({'errors': ['El usuario ya existe']}), 400

        usuario = Usuario(
            usuario=data['usuario'],
            contraseña=hash_password(data['contraseña']),
            fkSistema=data['fkSistema'],
            creado_por=data.get('creado_por'),
            estatus=BaseObjectEstatus.ACTIVO
        )

        db.session.add(usuario)
        db.session.commit()

        return jsonify(UsuarioSchema.serialize(usuario)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@usuario_bp.route('/many', methods=['POST'])
def create_many_usuarios():
    """Crea múltiples usuarios."""
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de usuarios']}), 400

        created = []
        errors = []
        for idx, item in enumerate(data):
            validation_errors = UsuarioSchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            if Usuario.query.filter_by(usuario=item['usuario']).first():
                errors.append({'index': idx, 'errors': ['El usuario ya existe']})
                continue
            usuario = Usuario(
                usuario=item['usuario'],
                contraseña=hash_password(item['contraseña']),
                fkSistema=item['fkSistema'],
                creado_por=item.get('creado_por'),
                estatus=BaseObjectEstatus.ACTIVO
            )
            db.session.add(usuario)
            created.append(usuario)

        if created:
            db.session.commit()

        response = {'created': len(created), 'data': UsuarioSchema.serialize_list(created)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@usuario_bp.route('/<string:oid>', methods=['PUT'])
def update_usuario(oid):
    """Actualiza un usuario."""
    try:
        usuario = Usuario.query.filter(
            Usuario.oid == oid,
            Usuario.estatus != BaseObjectEstatus.ELIMINADO
        ).first()

        if not usuario:
            return jsonify({'errors': ['Usuario no encontrado']}), 404

        data = request.get_json()

        errors = UsuarioSchema.validate_update(data)
        if errors:
            return jsonify({'errors': errors}), 422

        if 'usuario' in data:
            existing = Usuario.query.filter(
                Usuario.usuario == data['usuario'],
                Usuario.oid != oid
            ).first()
            if existing:
                return jsonify({'errors': ['El usuario ya existe']}), 400
            usuario.usuario = data['usuario']

        if 'contraseña' in data and data['contraseña']:
            usuario.contraseña = hash_password(data['contraseña'])

        if 'fkSistema' in data:
            usuario.fkSistema = data['fkSistema']

        if 'editado_por' in data:
            usuario.editado_por = data['editado_por']

        usuario.updatedAt = datetime.utcnow()

        db.session.commit()

        return jsonify(UsuarioSchema.serialize(usuario)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@usuario_bp.route('/many', methods=['PUT'])
def update_many_usuarios():
    """Actualiza múltiples usuarios."""
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de usuarios']}), 400

        updated = []
        errors = []
        for idx, item in enumerate(data):
            if 'oid' not in item:
                errors.append({'index': idx, 'errors': ['oid es requerido']})
                continue
            usuario = Usuario.query.filter(
                Usuario.oid == item['oid'],
                Usuario.estatus != BaseObjectEstatus.ELIMINADO
            ).first()
            if not usuario:
                errors.append({'index': idx, 'errors': ['Usuario no encontrado']})
                continue
            validation_errors = UsuarioSchema.validate_update(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue

            if 'usuario' in item:
                existing = Usuario.query.filter(
                    Usuario.usuario == item['usuario'],
                    Usuario.oid != usuario.oid
                ).first()
                if existing:
                    errors.append({'index': idx, 'errors': ['El usuario ya existe']})
                    continue
                usuario.usuario = item['usuario']
            if 'contraseña' in item and item['contraseña']:
                usuario.contraseña = hash_password(item['contraseña'])
            if 'fkSistema' in item:
                usuario.fkSistema = item['fkSistema']
            if 'editado_por' in item:
                usuario.editado_por = item['editado_por']

            usuario.updatedAt = datetime.utcnow()
            updated.append(usuario)

        if updated:
            db.session.commit()

        response = {'updated': len(updated), 'data': UsuarioSchema.serialize_list(updated)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@usuario_bp.route('/<string:oid>', methods=['DELETE'])
def delete_usuario(oid):
    """Soft delete de un usuario."""
    try:
        usuario = Usuario.query.filter(
            Usuario.oid == oid,
            Usuario.estatus != BaseObjectEstatus.ELIMINADO
        ).first()

        if not usuario:
            return jsonify({'errors': ['Usuario no encontrado']}), 404

        data = request.get_json() or {}
        usuario.estatus = BaseObjectEstatus.ELIMINADO
        usuario.editado_por = data.get('editado_por')
        usuario.updatedAt = datetime.utcnow()

        db.session.commit()

        return jsonify({'message': 'Usuario eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@usuario_bp.route('/list', methods=['POST'])
def get_usuario_list():
    """Lista de usuarios por OIDs (batch)."""
    try:
        data = request.get_json()

        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400

        oid_list = data.get('oid_list', [])

        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400

        usuarios = Usuario.query.filter(
            Usuario.oid.in_(oid_list),
            Usuario.estatus != BaseObjectEstatus.ELIMINADO
        ).all()

        return jsonify(UsuarioSchema.serialize_list(usuarios)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
