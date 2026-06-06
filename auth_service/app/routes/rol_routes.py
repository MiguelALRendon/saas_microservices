from flask import Blueprint, request, jsonify
from app import db
from app.models.rol import Rol
from app.schemas.rol_schema import RolSchema
from app.enums import BaseObjectEstatus
from datetime import datetime

rol_bp = Blueprint('rol', __name__, url_prefix='/rol')

# 1. GET /rol/<oid> - Obtener por OID
@rol_bp.route('/<string:oid>', methods=['GET'])
def get_rol(oid):
    """Obtiene un rol por su OID"""
    try:
        rol = Rol.query.filter(
            Rol.oid == oid,
            Rol.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not rol:
            return jsonify({'errors': ['Rol no encontrado']}), 404

        per_page = request.args.get('embedded_per_page', 25, type=int)
        return jsonify(RolSchema.serialize_detail(rol, per_page=per_page)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500

# 2. GET /rol/ - Listar con paginación y filtros
@rol_bp.route('/', methods=['GET'])
def get_roles():
    """Obtiene listado de roles con paginación y filtros"""
    try:
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Parámetros de filtrado
        nombre = request.args.get('nombre', type=str)
        
        # Query base - excluir eliminados
        query = Rol.query.filter(Rol.estatus != BaseObjectEstatus.ELIMINADO)
        
        # Aplicar filtros
        if nombre:
            query = query.filter(Rol.nombre.ilike(f'%{nombre}%'))
        
        # Paginación
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'data': RolSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500

# 3. POST /rol/ - Crear un rol
@rol_bp.route('/', methods=['POST'])
def create_rol():
    """Crea un nuevo rol"""
    try:
        data = request.get_json()
        
        # Validar datos
        errors = RolSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 422
        
        # Verificar unicidad
        if Rol.query.filter_by(nombre=data['nombre']).first():
            return jsonify({'errors': ['El nombre de rol ya existe']}), 400
        
        # Crear rol
        rol = Rol(
            nombre=data['nombre'],
            creado_por=data.get('creado_por'),
            estatus=BaseObjectEstatus.ACTIVO
        )
        
        db.session.add(rol)
        db.session.commit()
        
        return jsonify(RolSchema.serialize(rol)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500

# 4. PUT /rol/<oid> - Actualizar un rol
@rol_bp.route('/<string:oid>', methods=['PUT'])
def update_rol(oid):
    """Actualiza un rol"""
    try:
        rol = Rol.query.filter(
            Rol.oid == oid,
            Rol.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not rol:
            return jsonify({'errors': ['Rol no encontrado']}), 404
        
        data = request.get_json()
        
        # Validar datos
        errors = RolSchema.validate_update(data)
        if errors:
            return jsonify({'errors': errors}), 422
        
        # Actualizar campos
        if 'nombre' in data:
            # Verificar unicidad si se cambia el nombre
            existing = Rol.query.filter(
                Rol.nombre == data['nombre'],
                Rol.oid != oid
            ).first()
            if existing:
                return jsonify({'errors': ['El nombre de rol ya existe']}), 400
            rol.nombre = data['nombre']
        
        if 'editado_por' in data:
            rol.editado_por = data['editado_por']
        
        rol.updatedAt = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(RolSchema.serialize(rol)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500

# 5. DELETE /rol/<oid> - Eliminar (soft delete)
@rol_bp.route('/<string:oid>', methods=['DELETE'])
def delete_rol(oid):
    """Elimina (soft delete) un rol"""
    try:
        rol = Rol.query.filter(
            Rol.oid == oid,
            Rol.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not rol:
            return jsonify({'errors': ['Rol no encontrado']}), 404
        
        data = request.get_json()
        
        # Soft delete
        rol.estatus = BaseObjectEstatus.ELIMINADO
        rol.editado_por = data.get('editado_por') if data else None
        rol.updatedAt = datetime.utcnow()

        db.session.commit()

        return jsonify({'message': 'Rol eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


# 6. POST /rol/list - Obtener lista específica por OIDs
@rol_bp.route('/list', methods=['POST'])
def get_rol_list():
    """Obtiene una lista específica de roles a partir de un arreglo de OIDs"""
    try:
        data = request.get_json()

        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400

        oid_list = data.get('oid_list', [])

        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400

        roles = Rol.query.filter(
            Rol.oid.in_(oid_list),
            Rol.estatus != BaseObjectEstatus.ELIMINADO
        ).all()

        return jsonify(RolSchema.serialize_list(roles)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
