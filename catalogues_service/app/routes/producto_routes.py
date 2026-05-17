from flask import Blueprint, request, jsonify
from app import db
from app.models.producto import Producto
from app.schemas.producto_schema import ProductoSchema
from app.enums import BaseObjectEstatus, UnidadMedida
from datetime import datetime

producto_bp = Blueprint('producto', __name__, url_prefix='/producto')


@producto_bp.route('/<string:oid>', methods=['GET'])
def get_producto(oid):
    """Obtiene un producto por su OID"""
    try:
        producto = Producto.query.filter(
            Producto.oid == oid,
            Producto.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not producto:
            return jsonify({'errors': ['Producto no encontrado']}), 404
        
        return jsonify(ProductoSchema.serialize(producto)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@producto_bp.route('/', methods=['GET'])
def get_productos():
    """Obtiene listado de productos con paginación y filtros"""
    try:
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Parámetros de filtrado
        clave = request.args.get('clave', type=str)
        nombre = request.args.get('nombre', type=str)
        codigo_barras = request.args.get('codigo_barras', type=str)
        is_especial = request.args.get('is_especial', type=str)
        
        # Query base - excluir eliminados
        query = Producto.query.filter(Producto.estatus != BaseObjectEstatus.ELIMINADO)
        
        # Aplicar filtros
        if clave:
            query = query.filter(Producto.clave.ilike(f'%{clave}%'))
        if nombre:
            query = query.filter(Producto.nombre.ilike(f'%{nombre}%'))
        if codigo_barras:
            query = query.filter(Producto.codigo_barras.ilike(f'%{codigo_barras}%'))
        if is_especial:
            query = query.filter(Producto.is_especial == (is_especial.lower() == 'true'))
        
        # Paginación
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'data': ProductoSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@producto_bp.route('/', methods=['POST'])
def create_producto():
    """Crea un nuevo producto"""
    try:
        data = request.get_json()
        
        # Validar datos
        errors = ProductoSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Verificar que no exista la clave
        if Producto.query.filter_by(clave=data['clave']).first():
            return jsonify({'errors': ['La clave ya existe']}), 400
        
        # Verificar que no exista el código de barras si se proporciona
        if data.get('codigo_barras'):
            if Producto.query.filter_by(codigo_barras=data['codigo_barras']).first():
                return jsonify({'errors': ['El código de barras ya existe']}), 400
        
        # Convertir unidadMedida a enum
        unidad_medida = UnidadMedida[data['unidadMedida'].upper()] if isinstance(data['unidadMedida'], str) else data['unidadMedida']
        
        # Crear producto
        producto = Producto(
            clave=data['clave'],
            nombre=data['nombre'],
            codigo_barras=data.get('codigo_barras'),
            unidadMedida=unidad_medida,
            is_especial=data.get('is_especial', False),
            fkProveedorMarca=data['fkProveedorMarca'],
            creado_por=data.get('creado_por'),
            estatus=BaseObjectEstatus.ACTIVO
        )
        
        db.session.add(producto)
        db.session.commit()
        
        return jsonify(ProductoSchema.serialize(producto)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@producto_bp.route('/many', methods=['POST'])
def create_many_productos():
    """Crea múltiples productos"""
    try:
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de productos']}), 400
        
        productos_creados = []
        errors = []
        
        for idx, item in enumerate(data):
            # Validar datos
            validation_errors = ProductoSchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            
            # Verificar que no exista la clave
            if Producto.query.filter_by(clave=item['clave']).first():
                errors.append({'index': idx, 'errors': ['La clave ya existe']})
                continue
            
            # Verificar que no exista el código de barras si se proporciona
            if item.get('codigo_barras'):
                if Producto.query.filter_by(codigo_barras=item['codigo_barras']).first():
                    errors.append({'index': idx, 'errors': ['El código de barras ya existe']})
                    continue
            
            # Convertir unidadMedida a enum
            unidad_medida = UnidadMedida[item['unidadMedida'].upper()] if isinstance(item['unidadMedida'], str) else item['unidadMedida']
            
            # Crear producto
            producto = Producto(
                clave=item['clave'],
                nombre=item['nombre'],
                codigo_barras=item.get('codigo_barras'),
                unidadMedida=unidad_medida,
                is_especial=item.get('is_especial', False),
                fkProveedorMarca=item['fkProveedorMarca'],
                creado_por=item.get('creado_por'),
                estatus=BaseObjectEstatus.ACTIVO
            )
            
            db.session.add(producto)
            productos_creados.append(producto)
        
        if productos_creados:
            db.session.commit()
        
        response = {
            'created': len(productos_creados),
            'data': ProductoSchema.serialize_list(productos_creados)
        }
        
        if errors:
            response['errors'] = errors
        
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@producto_bp.route('/<string:oid>', methods=['PUT'])
def update_producto(oid):
    """Actualiza un producto"""
    try:
        producto = Producto.query.filter(
            Producto.oid == oid,
            Producto.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not producto:
            return jsonify({'errors': ['Producto no encontrado']}), 404
        
        data = request.get_json()
        
        # Validar datos
        errors = ProductoSchema.validate_update(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Actualizar campos
        if 'clave' in data:
            # Verificar que la clave no exista en otro producto
            existing = Producto.query.filter(
                Producto.clave == data['clave'],
                Producto.oid != oid
            ).first()
            if existing:
                return jsonify({'errors': ['La clave ya existe']}), 400
            producto.clave = data['clave']
        
        if 'codigo_barras' in data:
            # Verificar que el código de barras no exista en otro producto
            if data['codigo_barras']:
                existing = Producto.query.filter(
                    Producto.codigo_barras == data['codigo_barras'],
                    Producto.oid != oid
                ).first()
                if existing:
                    return jsonify({'errors': ['El código de barras ya existe']}), 400
            producto.codigo_barras = data['codigo_barras']
        
        if 'nombre' in data:
            producto.nombre = data['nombre']
        if 'unidadMedida' in data:
            producto.unidadMedida = UnidadMedida[data['unidadMedida'].upper()] if isinstance(data['unidadMedida'], str) else data['unidadMedida']
        if 'is_especial' in data:
            producto.is_especial = data['is_especial']
        if 'fkProveedorMarca' in data:
            producto.fkProveedorMarca = data['fkProveedorMarca']
        if 'editado_por' in data:
            producto.editado_por = data['editado_por']
        
        producto.updatedAt = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(ProductoSchema.serialize(producto)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@producto_bp.route('/many', methods=['PUT'])
def update_many_productos():
    """Actualiza múltiples productos"""
    try:
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de productos']}), 400
        
        productos_actualizados = []
        errors = []
        
        for idx, item in enumerate(data):
            if 'oid' not in item:
                errors.append({'index': idx, 'errors': ['oid es requerido']})
                continue
            
            producto = Producto.query.filter(
                Producto.oid == item['oid'],
                Producto.estatus != BaseObjectEstatus.ELIMINADO
            ).first()
            
            if not producto:
                errors.append({'index': idx, 'errors': ['Producto no encontrado']})
                continue
            
            # Validar datos
            validation_errors = ProductoSchema.validate_update(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            
            # Actualizar campos
            if 'clave' in item:
                existing = Producto.query.filter(
                    Producto.clave == item['clave'],
                    Producto.oid != item['oid']
                ).first()
                if existing:
                    errors.append({'index': idx, 'errors': ['La clave ya existe']})
                    continue
                producto.clave = item['clave']
            
            if 'codigo_barras' in item:
                if item['codigo_barras']:
                    existing = Producto.query.filter(
                        Producto.codigo_barras == item['codigo_barras'],
                        Producto.oid != item['oid']
                    ).first()
                    if existing:
                        errors.append({'index': idx, 'errors': ['El código de barras ya existe']})
                        continue
                producto.codigo_barras = item['codigo_barras']
            
            if 'nombre' in item:
                producto.nombre = item['nombre']
            if 'unidadMedida' in item:
                producto.unidadMedida = UnidadMedida[item['unidadMedida'].upper()] if isinstance(item['unidadMedida'], str) else item['unidadMedida']
            if 'is_especial' in item:
                producto.is_especial = item['is_especial']
            if 'fkProveedorMarca' in item:
                producto.fkProveedorMarca = item['fkProveedorMarca']
            if 'editado_por' in item:
                producto.editado_por = item['editado_por']
            
            producto.updatedAt = datetime.utcnow()
            productos_actualizados.append(producto)
        
        if productos_actualizados:
            db.session.commit()
        
        response = {
            'updated': len(productos_actualizados),
            'data': ProductoSchema.serialize_list(productos_actualizados)
        }
        
        if errors:
            response['errors'] = errors
        
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@producto_bp.route('/<string:oid>', methods=['DELETE'])
def delete_producto(oid):
    """Marca un producto como eliminado (soft delete)"""
    try:
        producto = Producto.query.filter(
            Producto.oid == oid,
            Producto.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not producto:
            return jsonify({'errors': ['Producto no encontrado']}), 404
        
        # Obtener el usuario que elimina (si se envía)
        data = request.get_json() or {}
        if 'editado_por' in data:
            producto.editado_por = data['editado_por']
        
        producto.estatus = BaseObjectEstatus.ELIMINADO
        producto.updatedAt = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Producto eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@producto_bp.route('/list', methods=['POST'])
def get_producto_list():
    """Obtiene una lista específica de productos a partir de un arreglo de OIDs"""
    try:
        data = request.get_json()
        
        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400
        
        oid_list = data.get('oid_list', [])
        
        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400
        
        productos = Producto.query.filter(
            Producto.oid.in_(oid_list),
            Producto.estatus != BaseObjectEstatus.ELIMINADO
        ).all()
        
        return jsonify(ProductoSchema.serialize_list(productos)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
