from flask import Blueprint, request, jsonify
from app import db
from app.models.sistema import Sistema
from app.schemas.sistema_schema import SistemaSchema
from app.enums import BaseObjectEstatus
from datetime import datetime

sistema_bp = Blueprint('sistema', __name__, url_prefix='/sistema')


@sistema_bp.route('/<string:oid>', methods=['GET'])
def get_sistema(oid):
    """Obtiene un sistema por su OID"""
    try:
        sistema = Sistema.query.filter(
            Sistema.oid == oid,
            Sistema.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not sistema:
            return jsonify({'errors': ['Sistema no encontrado']}), 404
        
        return jsonify(SistemaSchema.serialize(sistema)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@sistema_bp.route('/', methods=['GET'])
def get_sistemas():
    """Obtiene listado de sistemas con paginación y filtros"""
    try:
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Parámetros de filtrado
        clave = request.args.get('clave', type=str)
        nombre = request.args.get('nombre', type=str)
        
        # Query base - excluir eliminados
        query = Sistema.query.filter(Sistema.estatus != BaseObjectEstatus.ELIMINADO)
        
        # Aplicar filtros
        if clave:
            query = query.filter(Sistema.clave.ilike(f'%{clave}%'))
        if nombre:
            query = query.filter(Sistema.nombre.ilike(f'%{nombre}%'))
        
        # Paginación
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'data': SistemaSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@sistema_bp.route('/', methods=['POST'])
def create_sistema():
    """Crea un nuevo sistema"""
    try:
        data = request.get_json()
        
        # Validar datos
        errors = SistemaSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Verificar que no exista la clave
        if Sistema.query.filter_by(clave=data['clave']).first():
            return jsonify({'errors': ['La clave ya existe']}), 400
        
        # Verificar que no exista el api_key
        if Sistema.query.filter_by(api_key=data['api_key']).first():
            return jsonify({'errors': ['El api_key ya existe']}), 400
        
        # Crear sistema
        sistema = Sistema(
            clave=data['clave'],
            nombre=data['nombre'],
            descripcion=data.get('descripcion'),
            api_key=data['api_key'],
            creado_por=data.get('creado_por'),
            estatus=BaseObjectEstatus.ACTIVO
        )
        
        db.session.add(sistema)
        db.session.commit()
        
        return jsonify(SistemaSchema.serialize(sistema)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@sistema_bp.route('/many', methods=['POST'])
def create_many_sistemas():
    """Crea múltiples sistemas"""
    try:
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de sistemas']}), 400
        
        sistemas_creados = []
        errors = []
        
        for idx, item in enumerate(data):
            # Validar datos
            validation_errors = SistemaSchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            
            # Verificar que no exista la clave
            if Sistema.query.filter_by(clave=item['clave']).first():
                errors.append({'index': idx, 'errors': ['La clave ya existe']})
                continue
            
            # Verificar que no exista el api_key
            if Sistema.query.filter_by(api_key=item['api_key']).first():
                errors.append({'index': idx, 'errors': ['El api_key ya existe']})
                continue
            
            # Crear sistema
            sistema = Sistema(
                clave=item['clave'],
                nombre=item['nombre'],
                descripcion=item.get('descripcion'),
                api_key=item['api_key'],
                creado_por=item.get('creado_por'),
                estatus=BaseObjectEstatus.ACTIVO
            )
            
            db.session.add(sistema)
            sistemas_creados.append(sistema)
        
        if sistemas_creados:
            db.session.commit()
        
        response = {
            'created': len(sistemas_creados),
            'data': SistemaSchema.serialize_list(sistemas_creados)
        }
        
        if errors:
            response['errors'] = errors
        
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@sistema_bp.route('/<string:oid>', methods=['PUT'])
def update_sistema(oid):
    """Actualiza un sistema"""
    try:
        sistema = Sistema.query.filter(
            Sistema.oid == oid,
            Sistema.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not sistema:
            return jsonify({'errors': ['Sistema no encontrado']}), 404
        
        data = request.get_json()
        
        # Validar datos
        errors = SistemaSchema.validate_update(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Actualizar campos
        if 'clave' in data:
            # Verificar que la clave no exista en otro sistema
            existing = Sistema.query.filter(
                Sistema.clave == data['clave'],
                Sistema.oid != oid
            ).first()
            if existing:
                return jsonify({'errors': ['La clave ya existe']}), 400
            sistema.clave = data['clave']
        
        if 'api_key' in data:
            # Verificar que el api_key no exista en otro sistema
            existing = Sistema.query.filter(
                Sistema.api_key == data['api_key'],
                Sistema.oid != oid
            ).first()
            if existing:
                return jsonify({'errors': ['El api_key ya existe']}), 400
            sistema.api_key = data['api_key']
        
        if 'nombre' in data:
            sistema.nombre = data['nombre']
        if 'descripcion' in data:
            sistema.descripcion = data['descripcion']
        if 'editado_por' in data:
            sistema.editado_por = data['editado_por']
        
        sistema.updatedAt = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(SistemaSchema.serialize(sistema)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@sistema_bp.route('/many', methods=['PUT'])
def update_many_sistemas():
    """Actualiza múltiples sistemas"""
    try:
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de sistemas']}), 400
        
        sistemas_actualizados = []
        errors = []
        
        for idx, item in enumerate(data):
            if 'oid' not in item:
                errors.append({'index': idx, 'errors': ['oid es requerido']})
                continue
            
            sistema = Sistema.query.filter(
                Sistema.oid == item['oid'],
                Sistema.estatus != BaseObjectEstatus.ELIMINADO
            ).first()
            
            if not sistema:
                errors.append({'index': idx, 'errors': ['Sistema no encontrado']})
                continue
            
            # Validar datos
            validation_errors = SistemaSchema.validate_update(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            
            # Actualizar campos
            if 'clave' in item:
                existing = Sistema.query.filter(
                    Sistema.clave == item['clave'],
                    Sistema.oid != item['oid']
                ).first()
                if existing:
                    errors.append({'index': idx, 'errors': ['La clave ya existe']})
                    continue
                sistema.clave = item['clave']
            
            if 'api_key' in item:
                existing = Sistema.query.filter(
                    Sistema.api_key == item['api_key'],
                    Sistema.oid != item['oid']
                ).first()
                if existing:
                    errors.append({'index': idx, 'errors': ['El api_key ya existe']})
                    continue
                sistema.api_key = item['api_key']
            
            if 'nombre' in item:
                sistema.nombre = item['nombre']
            if 'descripcion' in item:
                sistema.descripcion = item['descripcion']
            if 'editado_por' in item:
                sistema.editado_por = item['editado_por']
            
            sistema.updatedAt = datetime.utcnow()
            sistemas_actualizados.append(sistema)
        
        if sistemas_actualizados:
            db.session.commit()
        
        response = {
            'updated': len(sistemas_actualizados),
            'data': SistemaSchema.serialize_list(sistemas_actualizados)
        }
        
        if errors:
            response['errors'] = errors
        
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@sistema_bp.route('/<string:oid>', methods=['DELETE'])
def delete_sistema(oid):
    """Marca un sistema como eliminado (soft delete)"""
    try:
        sistema = Sistema.query.filter(
            Sistema.oid == oid,
            Sistema.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not sistema:
            return jsonify({'errors': ['Sistema no encontrado']}), 404
        
        # Obtener el usuario que elimina (si se envía)
        data = request.get_json() or {}
        if 'editado_por' in data:
            sistema.editado_por = data['editado_por']
        
        sistema.estatus = BaseObjectEstatus.ELIMINADO
        sistema.updatedAt = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Sistema eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@sistema_bp.route('/list', methods=['POST'])
def get_sistema_list():
    """Obtiene una lista específica de sistemas a partir de un arreglo de OIDs"""
    try:
        data = request.get_json()
        
        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400
        
        oid_list = data.get('oid_list', [])
        
        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400
        
        sistemas = Sistema.query.filter(
            Sistema.oid.in_(oid_list),
            Sistema.estatus != BaseObjectEstatus.ELIMINADO
        ).all()
        
        return jsonify(SistemaSchema.serialize_list(sistemas)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
