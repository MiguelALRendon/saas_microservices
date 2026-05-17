from flask import Blueprint, request, jsonify
from app import db
from app.models.sucursal import Sucursal
from app.schemas.sucursal_schema import SucursalSchema
from app.enums import BaseObjectEstatus
from datetime import datetime

sucursal_bp = Blueprint('sucursal', __name__, url_prefix='/sucursal')


@sucursal_bp.route('/<string:oid>', methods=['GET'])
def get_sucursal(oid):
    """Obtiene una sucursal por su OID"""
    try:
        sucursal = Sucursal.query.filter(
            Sucursal.oid == oid,
            Sucursal.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not sucursal:
            return jsonify({'errors': ['Sucursal no encontrada']}), 404
        
        return jsonify(SucursalSchema.serialize(sucursal)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@sucursal_bp.route('/', methods=['GET'])
def get_sucursales():
    """Obtiene listado de sucursales con paginación y filtros"""
    try:
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Parámetros de filtrado
        clave = request.args.get('clave', type=str)
        nombre = request.args.get('nombre', type=str)
        fkEmpresa = request.args.get('fkEmpresa', type=str)
        
        # Query base - excluir eliminados
        query = Sucursal.query.filter(Sucursal.estatus != BaseObjectEstatus.ELIMINADO)
        
        # Aplicar filtros
        if clave:
            query = query.filter(Sucursal.clave.ilike(f'%{clave}%'))
        if nombre:
            query = query.filter(Sucursal.nombre.ilike(f'%{nombre}%'))
        if fkEmpresa:
            query = query.filter(Sucursal.fkEmpresa == fkEmpresa)
        
        # Paginación
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'data': SucursalSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@sucursal_bp.route('/', methods=['POST'])
def create_sucursal():
    """Crea una nueva sucursal"""
    try:
        data = request.get_json()
        
        # Validar datos
        errors = SucursalSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Verificar que no exista la clave
        if Sucursal.query.filter_by(clave=data['clave']).first():
            return jsonify({'errors': ['La clave ya existe']}), 400
        
        # Crear sucursal
        sucursal = Sucursal(
            clave=data['clave'],
            nombre=data['nombre'],
            folio=data['folio'],
            direccion=data['direccion'],
            telefono=data.get('telefono'),
            fkEmpresa=data['fkEmpresa'],
            creado_por=data.get('creado_por'),
            estatus=BaseObjectEstatus.ACTIVO
        )
        
        db.session.add(sucursal)
        db.session.commit()
        
        return jsonify(SucursalSchema.serialize(sucursal)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@sucursal_bp.route('/many', methods=['POST'])
def create_many_sucursales():
    """Crea múltiples sucursales"""
    try:
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de sucursales']}), 400
        
        sucursales_creadas = []
        errors = []
        
        for idx, item in enumerate(data):
            # Validar datos
            validation_errors = SucursalSchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            
            # Verificar que no exista la clave
            if Sucursal.query.filter_by(clave=item['clave']).first():
                errors.append({'index': idx, 'errors': ['La clave ya existe']})
                continue
            
            # Crear sucursal
            sucursal = Sucursal(
                clave=item['clave'],
                nombre=item['nombre'],
                folio=item['folio'],
                direccion=item['direccion'],
                telefono=item.get('telefono'),
                fkEmpresa=item['fkEmpresa'],
                creado_por=item.get('creado_por'),
                estatus=BaseObjectEstatus.ACTIVO
            )
            
            db.session.add(sucursal)
            sucursales_creadas.append(sucursal)
        
        if sucursales_creadas:
            db.session.commit()
        
        response = {
            'created': len(sucursales_creadas),
            'data': SucursalSchema.serialize_list(sucursales_creadas)
        }
        
        if errors:
            response['errors'] = errors
        
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@sucursal_bp.route('/<string:oid>', methods=['PUT'])
def update_sucursal(oid):
    """Actualiza una sucursal"""
    try:
        sucursal = Sucursal.query.filter(
            Sucursal.oid == oid,
            Sucursal.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not sucursal:
            return jsonify({'errors': ['Sucursal no encontrada']}), 404
        
        data = request.get_json()
        
        # Validar datos
        errors = SucursalSchema.validate_update(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Actualizar campos
        if 'clave' in data:
            # Verificar que la clave no exista en otra sucursal
            existing = Sucursal.query.filter(
                Sucursal.clave == data['clave'],
                Sucursal.oid != oid
            ).first()
            if existing:
                return jsonify({'errors': ['La clave ya existe']}), 400
            sucursal.clave = data['clave']
        
        if 'nombre' in data:
            sucursal.nombre = data['nombre']
        if 'folio' in data:
            sucursal.folio = data['folio']
        if 'direccion' in data:
            sucursal.direccion = data['direccion']
        if 'telefono' in data:
            sucursal.telefono = data['telefono']
        if 'fkEmpresa' in data:
            sucursal.fkEmpresa = data['fkEmpresa']
        if 'editado_por' in data:
            sucursal.editado_por = data['editado_por']
        
        sucursal.updatedAt = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(SucursalSchema.serialize(sucursal)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@sucursal_bp.route('/many', methods=['PUT'])
def update_many_sucursales():
    """Actualiza múltiples sucursales"""
    try:
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de sucursales']}), 400
        
        sucursales_actualizadas = []
        errors = []
        
        for idx, item in enumerate(data):
            if 'oid' not in item:
                errors.append({'index': idx, 'errors': ['oid es requerido']})
                continue
            
            sucursal = Sucursal.query.filter(
                Sucursal.oid == item['oid'],
                Sucursal.estatus != BaseObjectEstatus.ELIMINADO
            ).first()
            
            if not sucursal:
                errors.append({'index': idx, 'errors': ['Sucursal no encontrada']})
                continue
            
            # Validar datos
            validation_errors = SucursalSchema.validate_update(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            
            # Actualizar campos
            if 'clave' in item:
                existing = Sucursal.query.filter(
                    Sucursal.clave == item['clave'],
                    Sucursal.oid != item['oid']
                ).first()
                if existing:
                    errors.append({'index': idx, 'errors': ['La clave ya existe']})
                    continue
                sucursal.clave = item['clave']
            
            if 'nombre' in item:
                sucursal.nombre = item['nombre']
            if 'folio' in item:
                sucursal.folio = item['folio']
            if 'direccion' in item:
                sucursal.direccion = item['direccion']
            if 'telefono' in item:
                sucursal.telefono = item['telefono']
            if 'fkEmpresa' in item:
                sucursal.fkEmpresa = item['fkEmpresa']
            if 'editado_por' in item:
                sucursal.editado_por = item['editado_por']
            
            sucursal.updatedAt = datetime.utcnow()
            sucursales_actualizadas.append(sucursal)
        
        if sucursales_actualizadas:
            db.session.commit()
        
        response = {
            'updated': len(sucursales_actualizadas),
            'data': SucursalSchema.serialize_list(sucursales_actualizadas)
        }
        
        if errors:
            response['errors'] = errors
        
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@sucursal_bp.route('/<string:oid>', methods=['DELETE'])
def delete_sucursal(oid):
    """Marca una sucursal como eliminada (soft delete)"""
    try:
        sucursal = Sucursal.query.filter(
            Sucursal.oid == oid,
            Sucursal.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not sucursal:
            return jsonify({'errors': ['Sucursal no encontrada']}), 404
        
        # Obtener el usuario que elimina (si se envía)
        data = request.get_json() or {}
        if 'editado_por' in data:
            sucursal.editado_por = data['editado_por']
        
        sucursal.estatus = BaseObjectEstatus.ELIMINADO
        sucursal.updatedAt = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Sucursal eliminada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@sucursal_bp.route('/list', methods=['POST'])
def get_sucursal_list():
    """Obtiene una lista específica de sucursales a partir de un arreglo de OIDs"""
    try:
        data = request.get_json()
        
        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400
        
        oid_list = data.get('oid_list', [])
        
        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400
        
        sucursales = Sucursal.query.filter(
            Sucursal.oid.in_(oid_list),
            Sucursal.estatus != BaseObjectEstatus.ELIMINADO
        ).all()
        
        return jsonify(SucursalSchema.serialize_list(sucursales)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
