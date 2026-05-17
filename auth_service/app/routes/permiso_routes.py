from flask import Blueprint, request, jsonify
from app import db
from app.models.permiso_nuevo import Permiso
from app.schemas.permiso_schema import PermisoSchema
from app.enums import BaseObjectEstatus
from datetime import datetime

permiso_bp = Blueprint('permiso', __name__, url_prefix='/permiso')

# 1. GET /permiso/<oid> - Obtener por OID
@permiso_bp.route('/<string:oid>', methods=['GET'])
def get_permiso(oid):
    """Obtiene un permiso por su OID"""
    try:
        permiso = Permiso.query.filter(
            Permiso.oid == oid,
            Permiso.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not permiso:
            return jsonify({'errors': ['Permiso no encontrado']}), 404
        
        return jsonify(PermisoSchema.serialize(permiso)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500

# 2. GET /permiso/ - Listar con paginación y filtros
@permiso_bp.route('/', methods=['GET'])
def get_permisos():
    """Obtiene listado de permisos con paginación y filtros"""
    try:
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Parámetros de filtrado
        clave = request.args.get('clave', type=str)
        nombre = request.args.get('nombre', type=str)
        permiso = request.args.get('permiso', type=str)
        
        # Query base - excluir eliminados
        query = Permiso.query.filter(Permiso.estatus != BaseObjectEstatus.ELIMINADO)
        
        # Aplicar filtros
        if clave:
            query = query.filter(Permiso.clave.ilike(f'%{clave}%'))
        if nombre:
            query = query.filter(Permiso.nombre.ilike(f'%{nombre}%'))
        if permiso:
            query = query.filter(Permiso.permiso.ilike(f'%{permiso}%'))
        
        # Paginación
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'data': PermisoSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500

# 3. POST /permiso/ - Crear un permiso
@permiso_bp.route('/', methods=['POST'])
def create_permiso():
    """Crea un nuevo permiso"""
    try:
        data = request.get_json()
        
        # Validar datos
        errors = PermisoSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 422
        
        # Verificar unicidad
        if Permiso.query.filter_by(clave=data['clave']).first():
            return jsonify({'errors': ['La clave ya existe']}), 400
        
        # Crear permiso
        permiso = Permiso(
            clave=data['clave'],
            nombre=data['nombre'],
            permiso=data['permiso'],
            creado_por=data.get('creado_por'),
            estatus=BaseObjectEstatus.ACTIVO
        )
        
        db.session.add(permiso)
        db.session.commit()
        
        return jsonify(PermisoSchema.serialize(permiso)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500

# 4. POST /permiso/many - Crear múltiples permisos
@permiso_bp.route('/many', methods=['POST'])
def create_many_permisos():
    """Crea múltiples permisos"""
    try:
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de permisos']}), 400
        
        permisos_created = []
        errors = []
        
        for idx, item in enumerate(data):
            # Validar datos
            validation_errors = PermisoSchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            
            # Verificar unicidad
            if Permiso.query.filter_by(clave=item['clave']).first():
                errors.append({'index': idx, 'errors': ['La clave ya existe']})
                continue
            
            # Crear permiso
            permiso = Permiso(
                clave=item['clave'],
                nombre=item['nombre'],
                permiso=item['permiso'],
                creado_por=item.get('creado_por'),
                estatus=BaseObjectEstatus.ACTIVO
            )
            
            db.session.add(permiso)
            permisos_created.append(permiso)
        
        if permisos_created:
            db.session.commit()
        
        response = {
            'created': len(permisos_created),
            'data': PermisoSchema.serialize_list(permisos_created)
        }
        
        if errors:
            response['errors'] = errors
        
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500

# 5. PUT /permiso/<oid> - Actualizar un permiso
@permiso_bp.route('/<string:oid>', methods=['PUT'])
def update_permiso(oid):
    """Actualiza un permiso"""
    try:
        permiso = Permiso.query.filter(
            Permiso.oid == oid,
            Permiso.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not permiso:
            return jsonify({'errors': ['Permiso no encontrado']}), 404
        
        data = request.get_json()
        
        # Validar datos
        errors = PermisoSchema.validate_update(data)
        if errors:
            return jsonify({'errors': errors}), 422
        
        # Actualizar campos
        if 'clave' in data:
            # Verificar unicidad si se cambia la clave
            existing = Permiso.query.filter(
                Permiso.clave == data['clave'],
                Permiso.oid != oid
            ).first()
            if existing:
                return jsonify({'errors': ['La clave ya existe']}), 400
            permiso.clave = data['clave']
        
        if 'nombre' in data:
            permiso.nombre = data['nombre']
        
        if 'permiso' in data:
            permiso.permiso = data['permiso']
        
        if 'editado_por' in data:
            permiso.editado_por = data['editado_por']
        
        permiso.updatedAt = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(PermisoSchema.serialize(permiso)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500

# 6. PUT /permiso/many - Actualizar múltiples permisos
@permiso_bp.route('/many', methods=['PUT'])
def update_many_permisos():
    """Actualiza múltiples permisos"""
    try:
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de permisos']}), 400
        
        permisos_updated = []
        errors = []
        
        for idx, item in enumerate(data):
            if 'oid' not in item:
                errors.append({'index': idx, 'errors': ['oid es requerido']})
                continue
            
            permiso = Permiso.query.filter(
                Permiso.oid == item['oid'],
                Permiso.estatus != BaseObjectEstatus.ELIMINADO
            ).first()
            
            if not permiso:
                errors.append({'index': idx, 'errors': ['Permiso no encontrado']})
                continue
            
            # Validar datos
            validation_errors = PermisoSchema.validate_update(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            
            # Actualizar campos
            if 'nombre' in item:
                permiso.nombre = item['nombre']
            
            if 'permiso' in item:
                permiso.permiso = item['permiso']
            
            if 'editado_por' in item:
                permiso.editado_por = item['editado_por']
            
            permiso.updatedAt = datetime.utcnow()
            permisos_updated.append(permiso)
        
        if permisos_updated:
            db.session.commit()
        
        response = {
            'updated': len(permisos_updated),
            'data': PermisoSchema.serialize_list(permisos_updated)
        }
        
        if errors:
            response['errors'] = errors
        
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500

# 7. DELETE /permiso/<oid> - Eliminar (soft delete)
@permiso_bp.route('/<string:oid>', methods=['DELETE'])
def delete_permiso(oid):
    """Elimina (soft delete) un permiso"""
    try:
        permiso = Permiso.query.filter(
            Permiso.oid == oid,
            Permiso.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not permiso:
            return jsonify({'errors': ['Permiso no encontrado']}), 404
        
        data = request.get_json()
        
        # Soft delete
        permiso.estatus = BaseObjectEstatus.ELIMINADO
        permiso.editado_por = data.get('editado_por') if data else None
        permiso.updatedAt = datetime.utcnow()

        db.session.commit()

        return jsonify({'message': 'Permiso eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


# 8. POST /permiso/list - Obtener lista específica por OIDs
@permiso_bp.route('/list', methods=['POST'])
def get_permiso_list():
    """Obtiene una lista específica de permisos a partir de un arreglo de OIDs"""
    try:
        data = request.get_json()

        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400

        oid_list = data.get('oid_list', [])

        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400

        permisos = Permiso.query.filter(
            Permiso.oid.in_(oid_list),
            Permiso.estatus != BaseObjectEstatus.ELIMINADO
        ).all()

        return jsonify(PermisoSchema.serialize_list(permisos)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
