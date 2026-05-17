from flask import Blueprint, request, jsonify
from app import db
from app.models.empresa import Empresa
from app.schemas.empresa_schema import EmpresaSchema
from app.enums import BaseObjectEstatus
from datetime import datetime

empresa_bp = Blueprint('empresa', __name__, url_prefix='/empresa')


@empresa_bp.route('/<string:oid>', methods=['GET'])
def get_empresa(oid):
    """Obtiene una empresa por su OID"""
    try:
        empresa = Empresa.query.filter(
            Empresa.oid == oid,
            Empresa.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not empresa:
            return jsonify({'errors': ['Empresa no encontrada']}), 404
        
        return jsonify(EmpresaSchema.serialize(empresa)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@empresa_bp.route('/', methods=['GET'])
def get_empresas():
    """Obtiene listado de empresas con paginación y filtros"""
    try:
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Parámetros de filtrado
        clave = request.args.get('clave', type=str)
        nombre = request.args.get('nombre', type=str)
        email = request.args.get('email', type=str)
        
        # Query base - excluir eliminados
        query = Empresa.query.filter(Empresa.estatus != BaseObjectEstatus.ELIMINADO)
        
        # Aplicar filtros
        if clave:
            query = query.filter(Empresa.clave.ilike(f'%{clave}%'))
        if nombre:
            query = query.filter(Empresa.nombre.ilike(f'%{nombre}%'))
        if email:
            query = query.filter(Empresa.email.ilike(f'%{email}%'))
        
        # Paginación
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'data': EmpresaSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@empresa_bp.route('/', methods=['POST'])
def create_empresa():
    """Crea una nueva empresa"""
    try:
        data = request.get_json()
        
        # Validar datos
        errors = EmpresaSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Verificar que no exista la clave
        if Empresa.query.filter_by(clave=data['clave']).first():
            return jsonify({'errors': ['La clave ya existe']}), 400
        
        # Crear empresa
        empresa = Empresa(
            clave=data['clave'],
            nombre=data['nombre'],
            folio=data['folio'],
            urlLogo=data['urlLogo'],
            direccion=data['direccion'],
            telefono=data.get('telefono'),
            email=data.get('email'),
            creado_por=data.get('creado_por'),
            estatus=BaseObjectEstatus.ACTIVO
        )
        
        db.session.add(empresa)
        db.session.commit()
        
        return jsonify(EmpresaSchema.serialize(empresa)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@empresa_bp.route('/many', methods=['POST'])
def create_many_empresas():
    """Crea múltiples empresas"""
    try:
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de empresas']}), 400
        
        empresas_creadas = []
        errors = []
        
        for idx, item in enumerate(data):
            # Validar datos
            validation_errors = EmpresaSchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            
            # Verificar que no exista la clave
            if Empresa.query.filter_by(clave=item['clave']).first():
                errors.append({'index': idx, 'errors': ['La clave ya existe']})
                continue
            
            # Crear empresa
            empresa = Empresa(
                clave=item['clave'],
                nombre=item['nombre'],
                folio=item['folio'],
                urlLogo=item['urlLogo'],
                direccion=item['direccion'],
                telefono=item.get('telefono'),
                email=item.get('email'),
                creado_por=item.get('creado_por'),
                estatus=BaseObjectEstatus.ACTIVO
            )
            
            db.session.add(empresa)
            empresas_creadas.append(empresa)
        
        if empresas_creadas:
            db.session.commit()
        
        response = {
            'created': len(empresas_creadas),
            'data': EmpresaSchema.serialize_list(empresas_creadas)
        }
        
        if errors:
            response['errors'] = errors
        
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@empresa_bp.route('/<string:oid>', methods=['PUT'])
def update_empresa(oid):
    """Actualiza una empresa"""
    try:
        empresa = Empresa.query.filter(
            Empresa.oid == oid,
            Empresa.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not empresa:
            return jsonify({'errors': ['Empresa no encontrada']}), 404
        
        data = request.get_json()
        
        # Validar datos
        errors = EmpresaSchema.validate_update(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Actualizar campos
        if 'clave' in data:
            # Verificar que la clave no exista en otra empresa
            existing = Empresa.query.filter(
                Empresa.clave == data['clave'],
                Empresa.oid != oid
            ).first()
            if existing:
                return jsonify({'errors': ['La clave ya existe']}), 400
            empresa.clave = data['clave']
        
        if 'nombre' in data:
            empresa.nombre = data['nombre']
        if 'folio' in data:
            empresa.folio = data['folio']
        if 'urlLogo' in data:
            empresa.urlLogo = data['urlLogo']
        if 'direccion' in data:
            empresa.direccion = data['direccion']
        if 'telefono' in data:
            empresa.telefono = data['telefono']
        if 'email' in data:
            empresa.email = data['email']
        if 'editado_por' in data:
            empresa.editado_por = data['editado_por']
        
        empresa.updatedAt = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(EmpresaSchema.serialize(empresa)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@empresa_bp.route('/many', methods=['PUT'])
def update_many_empresas():
    """Actualiza múltiples empresas"""
    try:
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de empresas']}), 400
        
        empresas_actualizadas = []
        errors = []
        
        for idx, item in enumerate(data):
            if 'oid' not in item:
                errors.append({'index': idx, 'errors': ['oid es requerido']})
                continue
            
            empresa = Empresa.query.filter(
                Empresa.oid == item['oid'],
                Empresa.estatus != BaseObjectEstatus.ELIMINADO
            ).first()
            
            if not empresa:
                errors.append({'index': idx, 'errors': ['Empresa no encontrada']})
                continue
            
            # Validar datos
            validation_errors = EmpresaSchema.validate_update(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            
            # Actualizar campos
            if 'clave' in item:
                existing = Empresa.query.filter(
                    Empresa.clave == item['clave'],
                    Empresa.oid != item['oid']
                ).first()
                if existing:
                    errors.append({'index': idx, 'errors': ['La clave ya existe']})
                    continue
                empresa.clave = item['clave']
            
            if 'nombre' in item:
                empresa.nombre = item['nombre']
            if 'folio' in item:
                empresa.folio = item['folio']
            if 'urlLogo' in item:
                empresa.urlLogo = item['urlLogo']
            if 'direccion' in item:
                empresa.direccion = item['direccion']
            if 'telefono' in item:
                empresa.telefono = item['telefono']
            if 'email' in item:
                empresa.email = item['email']
            if 'editado_por' in item:
                empresa.editado_por = item['editado_por']
            
            empresa.updatedAt = datetime.utcnow()
            empresas_actualizadas.append(empresa)
        
        if empresas_actualizadas:
            db.session.commit()
        
        response = {
            'updated': len(empresas_actualizadas),
            'data': EmpresaSchema.serialize_list(empresas_actualizadas)
        }
        
        if errors:
            response['errors'] = errors
        
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@empresa_bp.route('/<string:oid>', methods=['DELETE'])
def delete_empresa(oid):
    """Marca una empresa como eliminada (soft delete)"""
    try:
        empresa = Empresa.query.filter(
            Empresa.oid == oid,
            Empresa.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not empresa:
            return jsonify({'errors': ['Empresa no encontrada']}), 404
        
        # Obtener el usuario que elimina (si se envía)
        data = request.get_json() or {}
        if 'editado_por' in data:
            empresa.editado_por = data['editado_por']
        
        empresa.estatus = BaseObjectEstatus.ELIMINADO
        empresa.updatedAt = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Empresa eliminada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@empresa_bp.route('/list', methods=['POST'])
def get_empresa_list():
    """Obtiene una lista específica de empresas a partir de un arreglo de OIDs"""
    try:
        data = request.get_json()
        
        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400
        
        oid_list = data.get('oid_list', [])
        
        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400
        
        empresas = Empresa.query.filter(
            Empresa.oid.in_(oid_list),
            Empresa.estatus != BaseObjectEstatus.ELIMINADO
        ).all()
        
        return jsonify(EmpresaSchema.serialize_list(empresas)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
