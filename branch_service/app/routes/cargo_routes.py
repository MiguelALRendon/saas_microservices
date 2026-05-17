from flask import Blueprint, request, jsonify
from app import db
from app.models.cargo import Cargo
from app.schemas.cargo_schema import CargoSchema
from app.enums import BaseObjectEstatus
from datetime import datetime

cargo_bp = Blueprint('cargo', __name__, url_prefix='/cargo')


@cargo_bp.route('/<string:oid>', methods=['GET'])
def get_cargo(oid):
    """Obtiene un cargo por su OID"""
    try:
        cargo = Cargo.query.filter(
            Cargo.oid == oid,
            Cargo.estatus != BaseObjectEstatus.ELIMINADO
        ).first()

        if not cargo:
            return jsonify({'errors': ['Cargo no encontrado']}), 404

        return jsonify(CargoSchema.serialize(cargo)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@cargo_bp.route('/', methods=['GET'])
def get_cargos():
    """Obtiene listado de cargos con paginación y filtros"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        clave = request.args.get('clave', type=str)
        nombre = request.args.get('nombre', type=str)

        query = Cargo.query.filter(Cargo.estatus != BaseObjectEstatus.ELIMINADO)

        if clave:
            query = query.filter(Cargo.clave.ilike(f'%{clave}%'))
        if nombre:
            query = query.filter(Cargo.nombre.ilike(f'%{nombre}%'))

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'data': CargoSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@cargo_bp.route('/', methods=['POST'])
def create_cargo():
    """Crea un nuevo cargo"""
    try:
        data = request.get_json()

        errors = CargoSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 400

        if Cargo.query.filter_by(clave=data['clave']).first():
            return jsonify({'errors': ['La clave ya existe']}), 400

        cargo = Cargo(
            clave=data['clave'],
            nombre=data['nombre'],
            creado_por=data.get('creado_por'),
            estatus=BaseObjectEstatus.ACTIVO
        )

        db.session.add(cargo)
        db.session.commit()

        return jsonify(CargoSchema.serialize(cargo)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@cargo_bp.route('/many', methods=['POST'])
def create_many_cargos():
    """Crea múltiples cargos"""
    try:
        data = request.get_json()

        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de cargos']}), 400

        cargos_created = []
        errors = []

        for idx, item in enumerate(data):
            validation_errors = CargoSchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue

            if Cargo.query.filter_by(clave=item['clave']).first():
                errors.append({'index': idx, 'errors': ['La clave ya existe']})
                continue

            cargo = Cargo(
                clave=item['clave'],
                nombre=item['nombre'],
                creado_por=item.get('creado_por'),
                estatus=BaseObjectEstatus.ACTIVO
            )

            db.session.add(cargo)
            cargos_created.append(cargo)

        if cargos_created:
            db.session.commit()

        response = {
            'created': len(cargos_created),
            'data': CargoSchema.serialize_list(cargos_created)
        }

        if errors:
            response['errors'] = errors

        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@cargo_bp.route('/<string:oid>', methods=['PUT'])
def update_cargo(oid):
    """Actualiza un cargo"""
    try:
        cargo = Cargo.query.filter(
            Cargo.oid == oid,
            Cargo.estatus != BaseObjectEstatus.ELIMINADO
        ).first()

        if not cargo:
            return jsonify({'errors': ['Cargo no encontrado']}), 404

        data = request.get_json()

        errors = CargoSchema.validate_update(data)
        if errors:
            return jsonify({'errors': errors}), 400

        if 'clave' in data:
            existing = Cargo.query.filter(
                Cargo.clave == data['clave'],
                Cargo.oid != oid
            ).first()
            if existing:
                return jsonify({'errors': ['La clave ya existe']}), 400
            cargo.clave = data['clave']

        if 'nombre' in data:
            cargo.nombre = data['nombre']

        if 'editado_por' in data:
            cargo.editado_por = data['editado_por']

        cargo.updatedAt = datetime.utcnow()

        db.session.commit()

        return jsonify(CargoSchema.serialize(cargo)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@cargo_bp.route('/many', methods=['PUT'])
def update_many_cargos():
    """Actualiza múltiples cargos"""
    try:
        data = request.get_json()

        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de cargos']}), 400

        cargos_updated = []
        errors = []

        for idx, item in enumerate(data):
            if 'oid' not in item:
                errors.append({'index': idx, 'errors': ['oid es requerido']})
                continue

            cargo = Cargo.query.filter(
                Cargo.oid == item['oid'],
                Cargo.estatus != BaseObjectEstatus.ELIMINADO
            ).first()

            if not cargo:
                errors.append({'index': idx, 'errors': ['Cargo no encontrado']})
                continue

            validation_errors = CargoSchema.validate_update(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue

            if 'nombre' in item:
                cargo.nombre = item['nombre']

            if 'editado_por' in item:
                cargo.editado_por = item['editado_por']

            cargo.updatedAt = datetime.utcnow()
            cargos_updated.append(cargo)

        if cargos_updated:
            db.session.commit()

        response = {
            'updated': len(cargos_updated),
            'data': CargoSchema.serialize_list(cargos_updated)
        }

        if errors:
            response['errors'] = errors

        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@cargo_bp.route('/<string:oid>', methods=['DELETE'])
def delete_cargo(oid):
    """Elimina (soft delete) un cargo"""
    try:
        cargo = Cargo.query.filter(
            Cargo.oid == oid,
            Cargo.estatus != BaseObjectEstatus.ELIMINADO
        ).first()

        if not cargo:
            return jsonify({'errors': ['Cargo no encontrado']}), 404

        data = request.get_json() or {}

        cargo.estatus = BaseObjectEstatus.ELIMINADO
        cargo.editado_por = data.get('editado_por')
        cargo.updatedAt = datetime.utcnow()

        db.session.commit()

        return jsonify({'message': 'Cargo eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@cargo_bp.route('/list', methods=['POST'])
def get_cargo_list():
    """Obtiene una lista específica de cargos a partir de un arreglo de OIDs"""
    try:
        data = request.get_json()

        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400

        oid_list = data.get('oid_list', [])

        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400

        cargos = Cargo.query.filter(
            Cargo.oid.in_(oid_list),
            Cargo.estatus != BaseObjectEstatus.ELIMINADO
        ).all()

        return jsonify(CargoSchema.serialize_list(cargos)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
