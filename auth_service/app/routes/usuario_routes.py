from flask import Blueprint, request, jsonify
from app import db
from app.models.usuario import Usuario
from app.schemas.usuario_schema import UsuarioSchema
from app.enums import BaseObjectEstatus
from app.utils import hash_password
from datetime import datetime

usuario_bp = Blueprint('usuario', __name__, url_prefix='/usuario')

# 1. GET /usuario/<oid> - Obtener por OID
@usuario_bp.route('/<string:oid>', methods=['GET'])
def get_usuario(oid):
    """Obtiene un usuario por su OID"""
    try:
        usuario = Usuario.query.filter(
            Usuario.oid == oid,
            Usuario.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not usuario:
            return jsonify({'errors': ['Usuario no encontrado']}), 404
        
        return jsonify(UsuarioSchema.serialize(usuario)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500

# 2. GET /usuario/ - Listar con paginación y filtros
@usuario_bp.route('/', methods=['GET'])
def get_usuarios():
    """Obtiene listado de usuarios con paginación y filtros"""
    try:
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Parámetros de filtrado
        usuario = request.args.get('usuario', type=str)
        fkEmpleado = request.args.get('fkEmpleado', type=str)
        
        # Query base - excluir eliminados
        query = Usuario.query.filter(Usuario.estatus != BaseObjectEstatus.ELIMINADO)
        
        # Aplicar filtros
        if usuario:
            query = query.filter(Usuario.usuario.ilike(f'%{usuario}%'))
        if fkEmpleado:
            query = query.filter(Usuario.fkEmpleado == fkEmpleado)
        
        # Paginación
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

# 3. POST /usuario/ - Crear un usuario
@usuario_bp.route('/', methods=['POST'])
def create_usuario():
    """Crea un nuevo usuario"""
    try:
        data = request.get_json()
        
        # Validar datos
        errors = UsuarioSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 422
        
        # Verificar unicidad
        if Usuario.query.filter_by(usuario=data['usuario']).first():
            return jsonify({'errors': ['El usuario ya existe']}), 400
        
        # Hashear contraseña con Argon2
        hashed_password = hash_password(data['contraseña'])
        
        # Crear usuario
        usuario = Usuario(
            usuario=data['usuario'],
            contraseña=hashed_password,
            fkSistema=data['fkSistema'],
            fkEmpleado=data['fkEmpleado'],
            creado_por=data.get('creado_por'),
            estatus=BaseObjectEstatus.ACTIVO
        )
        
        db.session.add(usuario)
        db.session.commit()
        
        return jsonify(UsuarioSchema.serialize(usuario)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500

# 4. PUT /usuario/<oid> - Actualizar un usuario
@usuario_bp.route('/<string:oid>', methods=['PUT'])
def update_usuario(oid):
    """Actualiza un usuario"""
    try:
        usuario = Usuario.query.filter(
            Usuario.oid == oid,
            Usuario.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not usuario:
            return jsonify({'errors': ['Usuario no encontrado']}), 404
        
        data = request.get_json()
        
        # Validar datos
        errors = UsuarioSchema.validate_update(data)
        if errors:
            return jsonify({'errors': errors}), 422
        
        # Actualizar campos
        if 'usuario' in data:
            # Verificar unicidad si se cambia el usuario
            existing = Usuario.query.filter(
                Usuario.usuario == data['usuario'],
                Usuario.oid != oid
            ).first()
            if existing:
                return jsonify({'errors': ['El usuario ya existe']}), 400
            usuario.usuario = data['usuario']
        
        if 'contraseña' in data:
            # Hashear la nueva contraseña con Argon2
            usuario.contraseña = hash_password(data['contraseña'])
        
        if 'fkSistema' in data:
            usuario.fkSistema = data['fkSistema']
        
        if 'fkEmpleado' in data:
            usuario.fkEmpleado = data['fkEmpleado']
        
        if 'editado_por' in data:
            usuario.editado_por = data['editado_por']
        
        usuario.updatedAt = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(UsuarioSchema.serialize(usuario)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500

# 5. DELETE /usuario/<oid> - Eliminar (soft delete)
@usuario_bp.route('/<string:oid>', methods=['DELETE'])
def delete_usuario(oid):
    """Elimina (soft delete) un usuario"""
    try:
        usuario = Usuario.query.filter(
            Usuario.oid == oid,
            Usuario.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not usuario:
            return jsonify({'errors': ['Usuario no encontrado']}), 404
        
        data = request.get_json()
        
        # Soft delete
        usuario.estatus = BaseObjectEstatus.ELIMINADO
        usuario.editado_por = data.get('editado_por') if data else None
        usuario.updatedAt = datetime.utcnow()

        db.session.commit()

        return jsonify({'message': 'Usuario eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


# 6. POST /usuario/list - Obtener lista específica por OIDs
@usuario_bp.route('/list', methods=['POST'])
def get_usuario_list():
    """Obtiene una lista específica de usuarios a partir de un arreglo de OIDs"""
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
