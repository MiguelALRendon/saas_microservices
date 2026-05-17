from flask import Blueprint, request, jsonify
from app import db
from app.models.usuario_rol import UsuarioRol
from app.schemas.usuario_rol_schema import UsuarioRolSchema
from app.enums import BaseObjectEstatus
from datetime import datetime

usuario_rol_bp = Blueprint('usuario_rol', __name__, url_prefix='/usuario_rol')

# 1. GET /usuario_rol/<oid> - Obtener por OID
@usuario_rol_bp.route('/<string:oid>', methods=['GET'])
def get_usuario_rol(oid):
    """Obtiene un usuario_rol por su OID"""
    try:
        usuario_rol = UsuarioRol.query.filter(
            UsuarioRol.oid == oid,
            UsuarioRol.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not usuario_rol:
            return jsonify({'errors': ['Usuario-Rol no encontrado']}), 404
        
        return jsonify(UsuarioRolSchema.serialize(usuario_rol)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500

# 2. GET /usuario_rol/ - Listar con paginación y filtros
@usuario_rol_bp.route('/', methods=['GET'])
def get_usuario_roles():
    """Obtiene listado de usuario_roles con paginación y filtros"""
    try:
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Parámetros de filtrado
        fkUsuario = request.args.get('fkUsuario', type=str)
        fkRol = request.args.get('fkRol', type=str)
        
        # Query base - excluir eliminados
        query = UsuarioRol.query.filter(UsuarioRol.estatus != BaseObjectEstatus.ELIMINADO)
        
        # Aplicar filtros
        if fkUsuario:
            query = query.filter(UsuarioRol.fkUsuario == fkUsuario)
        if fkRol:
            query = query.filter(UsuarioRol.fkRol == fkRol)
        
        # Paginación
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'data': UsuarioRolSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500

# 3. POST /usuario_rol/ - Crear un usuario_rol
@usuario_rol_bp.route('/', methods=['POST'])
def create_usuario_rol():
    """Crea un nuevo usuario_rol"""
    try:
        data = request.get_json()
        
        # Validar datos
        errors = UsuarioRolSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 422
        
        # Verificar unicidad (un usuario solo puede tener un rol una vez)
        existing = UsuarioRol.query.filter_by(
            fkUsuario=data['fkUsuario'],
            fkRol=data['fkRol']
        ).first()
        
        if existing:
            return jsonify({'errors': ['El rol ya está asignado a este usuario']}), 400
        
        # Crear usuario_rol
        usuario_rol = UsuarioRol(
            fkUsuario=data['fkUsuario'],
            fkRol=data['fkRol'],
            creado_por=data.get('creado_por'),
            estatus=BaseObjectEstatus.ACTIVO
        )
        
        db.session.add(usuario_rol)
        db.session.commit()
        
        return jsonify(UsuarioRolSchema.serialize(usuario_rol)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500

# 4. POST /usuario_rol/many - Crear múltiples usuario_roles
@usuario_rol_bp.route('/many', methods=['POST'])
def create_many_usuario_roles():
    """Crea múltiples usuario_roles"""
    try:
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de usuario_roles']}), 400
        
        usuario_roles_created = []
        errors = []
        
        for idx, item in enumerate(data):
            # Validar datos
            validation_errors = UsuarioRolSchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            
            # Verificar unicidad
            existing = UsuarioRol.query.filter_by(
                fkUsuario=item['fkUsuario'],
                fkRol=item['fkRol']
            ).first()
            
            if existing:
                errors.append({'index': idx, 'errors': ['El rol ya está asignado a este usuario']})
                continue
            
            # Crear usuario_rol
            usuario_rol = UsuarioRol(
                fkUsuario=item['fkUsuario'],
                fkRol=item['fkRol'],
                creado_por=item.get('creado_por'),
                estatus=BaseObjectEstatus.ACTIVO
            )
            
            db.session.add(usuario_rol)
            usuario_roles_created.append(usuario_rol)
        
        if usuario_roles_created:
            db.session.commit()
        
        response = {
            'created': len(usuario_roles_created),
            'data': UsuarioRolSchema.serialize_list(usuario_roles_created)
        }
        
        if errors:
            response['errors'] = errors
        
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500

# 5. PUT /usuario_rol/<oid> - Actualizar un usuario_rol
@usuario_rol_bp.route('/<string:oid>', methods=['PUT'])
def update_usuario_rol(oid):
    """Actualiza un usuario_rol"""
    try:
        usuario_rol = UsuarioRol.query.filter(
            UsuarioRol.oid == oid,
            UsuarioRol.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not usuario_rol:
            return jsonify({'errors': ['Usuario-Rol no encontrado']}), 404
        
        data = request.get_json()
        
        # Validar datos
        errors = UsuarioRolSchema.validate_update(data)
        if errors:
            return jsonify({'errors': errors}), 422
        
        # Actualizar campos
        if 'editado_por' in data:
            usuario_rol.editado_por = data['editado_por']
        
        usuario_rol.updatedAt = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(UsuarioRolSchema.serialize(usuario_rol)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500

# 6. PUT /usuario_rol/many - Actualizar múltiples usuario_roles
@usuario_rol_bp.route('/many', methods=['PUT'])
def update_many_usuario_roles():
    """Actualiza múltiples usuario_roles"""
    try:
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de usuario_roles']}), 400
        
        usuario_roles_updated = []
        errors = []
        
        for idx, item in enumerate(data):
            if 'oid' not in item:
                errors.append({'index': idx, 'errors': ['oid es requerido']})
                continue
            
            usuario_rol = UsuarioRol.query.filter(
                UsuarioRol.oid == item['oid'],
                UsuarioRol.estatus != BaseObjectEstatus.ELIMINADO
            ).first()
            
            if not usuario_rol:
                errors.append({'index': idx, 'errors': ['Usuario-Rol no encontrado']})
                continue
            
            # Validar datos
            validation_errors = UsuarioRolSchema.validate_update(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            
            # Actualizar campos
            if 'editado_por' in item:
                usuario_rol.editado_por = item['editado_por']
            
            usuario_rol.updatedAt = datetime.utcnow()
            usuario_roles_updated.append(usuario_rol)
        
        if usuario_roles_updated:
            db.session.commit()
        
        response = {
            'updated': len(usuario_roles_updated),
            'data': UsuarioRolSchema.serialize_list(usuario_roles_updated)
        }
        
        if errors:
            response['errors'] = errors
        
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500

# 7. DELETE /usuario_rol/<oid> - Eliminar (soft delete)
@usuario_rol_bp.route('/<string:oid>', methods=['DELETE'])
def delete_usuario_rol(oid):
    """Elimina (soft delete) un usuario_rol"""
    try:
        usuario_rol = UsuarioRol.query.filter(
            UsuarioRol.oid == oid,
            UsuarioRol.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not usuario_rol:
            return jsonify({'errors': ['Usuario-Rol no encontrado']}), 404
        
        data = request.get_json()
        
        # Soft delete
        usuario_rol.estatus = BaseObjectEstatus.ELIMINADO
        usuario_rol.editado_por = data.get('editado_por') if data else None
        usuario_rol.updatedAt = datetime.utcnow()

        db.session.commit()

        return jsonify({'message': 'Usuario-Rol eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


# 8. POST /usuario_rol/list - Obtener lista específica por OIDs
@usuario_rol_bp.route('/list', methods=['POST'])
def get_usuario_rol_list():
    """Obtiene una lista específica de usuario_roles a partir de un arreglo de OIDs"""
    try:
        data = request.get_json()

        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400

        oid_list = data.get('oid_list', [])

        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400

        usuario_roles = UsuarioRol.query.filter(
            UsuarioRol.oid.in_(oid_list),
            UsuarioRol.estatus != BaseObjectEstatus.ELIMINADO
        ).all()

        return jsonify(UsuarioRolSchema.serialize_list(usuario_roles)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
