from flask import Blueprint, request, jsonify
from app import db
from app.models.permiso_asignado import PermisoAsignado
from app.schemas.permiso_asignado_schema import PermisoAsignadoSchema
from app.enums import BaseObjectEstatus
from datetime import datetime

permiso_asignado_bp = Blueprint('permiso_asignado', __name__, url_prefix='/permiso_asignado')

# 1. GET /permiso_asignado/<oid> - Obtener por OID
@permiso_asignado_bp.route('/<string:oid>', methods=['GET'])
def get_permiso_asignado(oid):
    """Obtiene un permiso asignado por su OID"""
    try:
        permiso_asignado = PermisoAsignado.query.filter(
            PermisoAsignado.oid == oid,
            PermisoAsignado.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not permiso_asignado:
            return jsonify({'errors': ['Permiso asignado no encontrado']}), 404
        
        return jsonify(PermisoAsignadoSchema.serialize(permiso_asignado)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500

# 2. GET /permiso_asignado/ - Listar con paginación y filtros
@permiso_asignado_bp.route('/', methods=['GET'])
def get_permisos_asignados():
    """Obtiene listado de permisos asignados con paginación y filtros"""
    try:
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Parámetros de filtrado
        fkRol = request.args.get('fkRol', type=str)
        fkPermiso = request.args.get('fkPermiso', type=str)
        
        # Query base - excluir eliminados
        query = PermisoAsignado.query.filter(PermisoAsignado.estatus != BaseObjectEstatus.ELIMINADO)
        
        # Aplicar filtros
        if fkRol:
            query = query.filter(PermisoAsignado.fkRol == fkRol)
        if fkPermiso:
            query = query.filter(PermisoAsignado.fkPermiso == fkPermiso)
        
        # Paginación
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'data': PermisoAsignadoSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500

# 3. POST /permiso_asignado/ - Crear un permiso asignado
@permiso_asignado_bp.route('/', methods=['POST'])
def create_permiso_asignado():
    """Crea un nuevo permiso asignado"""
    try:
        data = request.get_json()
        
        # Validar datos
        errors = PermisoAsignadoSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 422
        
        # Verificar unicidad (un permiso por rol solo una vez)
        existing = PermisoAsignado.query.filter_by(
            fkRol=data['fkRol'],
            fkPermiso=data['fkPermiso']
        ).first()
        
        if existing:
            return jsonify({'errors': ['El permiso ya está asignado a este rol']}), 400
        
        # Crear permiso asignado
        permiso_asignado = PermisoAsignado(
            fkPermiso=data['fkPermiso'],
            fkRol=data['fkRol'],
            crear=data.get('crear', False),
            editar=data.get('editar', False),
            desactivar=data.get('desactivar', False),
            cancelar=data.get('cancelar', False),
            creado_por=data.get('creado_por'),
            estatus=BaseObjectEstatus.ACTIVO
        )
        
        db.session.add(permiso_asignado)
        db.session.commit()
        
        return jsonify(PermisoAsignadoSchema.serialize(permiso_asignado)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500

# 4. POST /permiso_asignado/many - Crear múltiples permisos asignados
@permiso_asignado_bp.route('/many', methods=['POST'])
def create_many_permisos_asignados():
    """Crea múltiples permisos asignados"""
    try:
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de permisos asignados']}), 400
        
        permisos_asignados_created = []
        errors = []
        
        for idx, item in enumerate(data):
            # Validar datos
            validation_errors = PermisoAsignadoSchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            
            # Verificar unicidad
            existing = PermisoAsignado.query.filter_by(
                fkRol=item['fkRol'],
                fkPermiso=item['fkPermiso']
            ).first()
            
            if existing:
                errors.append({'index': idx, 'errors': ['El permiso ya está asignado a este rol']})
                continue
            
            # Crear permiso asignado
            permiso_asignado = PermisoAsignado(
                fkPermiso=item['fkPermiso'],
                fkRol=item['fkRol'],
                crear=item.get('crear', False),
                editar=item.get('editar', False),
                desactivar=item.get('desactivar', False),
                cancelar=item.get('cancelar', False),
                creado_por=item.get('creado_por'),
                estatus=BaseObjectEstatus.ACTIVO
            )
            
            db.session.add(permiso_asignado)
            permisos_asignados_created.append(permiso_asignado)
        
        if permisos_asignados_created:
            db.session.commit()
        
        response = {
            'created': len(permisos_asignados_created),
            'data': PermisoAsignadoSchema.serialize_list(permisos_asignados_created)
        }
        
        if errors:
            response['errors'] = errors
        
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500

# 5. PUT /permiso_asignado/<oid> - Actualizar un permiso asignado
@permiso_asignado_bp.route('/<string:oid>', methods=['PUT'])
def update_permiso_asignado(oid):
    """Actualiza un permiso asignado"""
    try:
        permiso_asignado = PermisoAsignado.query.filter(
            PermisoAsignado.oid == oid,
            PermisoAsignado.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not permiso_asignado:
            return jsonify({'errors': ['Permiso asignado no encontrado']}), 404
        
        data = request.get_json()
        
        # Validar datos
        errors = PermisoAsignadoSchema.validate_update(data)
        if errors:
            return jsonify({'errors': errors}), 422
        
        # Actualizar campos
        if 'crear' in data:
            permiso_asignado.crear = data['crear']
        
        if 'editar' in data:
            permiso_asignado.editar = data['editar']
        
        if 'desactivar' in data:
            permiso_asignado.desactivar = data['desactivar']
        
        if 'cancelar' in data:
            permiso_asignado.cancelar = data['cancelar']
        
        if 'editado_por' in data:
            permiso_asignado.editado_por = data['editado_por']
        
        permiso_asignado.updatedAt = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(PermisoAsignadoSchema.serialize(permiso_asignado)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500

# 6. PUT /permiso_asignado/many - Actualizar múltiples permisos asignados
@permiso_asignado_bp.route('/many', methods=['PUT'])
def update_many_permisos_asignados():
    """Actualiza múltiples permisos asignados"""
    try:
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de permisos asignados']}), 400
        
        permisos_asignados_updated = []
        errors = []
        
        for idx, item in enumerate(data):
            if 'oid' not in item:
                errors.append({'index': idx, 'errors': ['oid es requerido']})
                continue
            
            permiso_asignado = PermisoAsignado.query.filter(
                PermisoAsignado.oid == item['oid'],
                PermisoAsignado.estatus != BaseObjectEstatus.ELIMINADO
            ).first()
            
            if not permiso_asignado:
                errors.append({'index': idx, 'errors': ['Permiso asignado no encontrado']})
                continue
            
            # Validar datos
            validation_errors = PermisoAsignadoSchema.validate_update(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            
            # Actualizar campos
            if 'crear' in item:
                permiso_asignado.crear = item['crear']
            
            if 'editar' in item:
                permiso_asignado.editar = item['editar']
            
            if 'desactivar' in item:
                permiso_asignado.desactivar = item['desactivar']
            
            if 'cancelar' in item:
                permiso_asignado.cancelar = item['cancelar']
            
            if 'editado_por' in item:
                permiso_asignado.editado_por = item['editado_por']
            
            permiso_asignado.updatedAt = datetime.utcnow()
            permisos_asignados_updated.append(permiso_asignado)
        
        if permisos_asignados_updated:
            db.session.commit()
        
        response = {
            'updated': len(permisos_asignados_updated),
            'data': PermisoAsignadoSchema.serialize_list(permisos_asignados_updated)
        }
        
        if errors:
            response['errors'] = errors
        
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500

# 7. DELETE /permiso_asignado/<oid> - Eliminar (soft delete)
@permiso_asignado_bp.route('/<string:oid>', methods=['DELETE'])
def delete_permiso_asignado(oid):
    """Elimina (soft delete) un permiso asignado"""
    try:
        permiso_asignado = PermisoAsignado.query.filter(
            PermisoAsignado.oid == oid,
            PermisoAsignado.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not permiso_asignado:
            return jsonify({'errors': ['Permiso asignado no encontrado']}), 404
        
        data = request.get_json()

        # Soft delete
        permiso_asignado.estatus = BaseObjectEstatus.ELIMINADO
        permiso_asignado.editado_por = data.get('editado_por') if data else None
        permiso_asignado.updatedAt = datetime.utcnow()

        db.session.commit()

        return jsonify({'message': 'Permiso asignado eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


# 8. POST /permiso_asignado/list - Obtener lista específica por OIDs
@permiso_asignado_bp.route('/list', methods=['POST'])
def get_permiso_asignado_list():
    """Obtiene una lista específica de permisos asignados a partir de un arreglo de OIDs"""
    try:
        data = request.get_json()

        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400

        oid_list = data.get('oid_list', [])

        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400

        permisos_asignados = PermisoAsignado.query.filter(
            PermisoAsignado.oid.in_(oid_list),
            PermisoAsignado.estatus != BaseObjectEstatus.ELIMINADO
        ).all()

        return jsonify(PermisoAsignadoSchema.serialize_list(permisos_asignados)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
