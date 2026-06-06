from flask import Blueprint, request, jsonify
from app import db
from app.models.empleado_sucursal import EmpleadoSucursal
from app.models.empleado import Empleado
from app.schemas.empleado_sucursal_schema import EmpleadoSucursalSchema
from app.enums import BaseObjectEstatus
from datetime import datetime

empleado_sucursal_bp = Blueprint('empleado_sucursal', __name__, url_prefix='/empleado-sucursal')


@empleado_sucursal_bp.route('/<string:oid>', methods=['GET'])
def get_empleado_sucursal(oid):
    try:
        item = EmpleadoSucursal.query.filter(
            EmpleadoSucursal.oid == oid,
            EmpleadoSucursal.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        if not item:
            return jsonify({'errors': ['Asignación no encontrada']}), 404
        return jsonify(EmpleadoSucursalSchema.serialize(item)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@empleado_sucursal_bp.route('/', methods=['GET'])
def get_empleado_sucursales():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        fk_empleado = request.args.get('fkEmpleado', type=str)
        fk_sucursal = request.args.get('fkSucursal', type=str)

        query = EmpleadoSucursal.query.filter(EmpleadoSucursal.estatus != BaseObjectEstatus.ELIMINADO)
        if fk_empleado:
            query = query.filter(EmpleadoSucursal.fkEmpleado == fk_empleado)
        if fk_sucursal:
            query = query.filter(EmpleadoSucursal.fkSucursal == fk_sucursal)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'data': EmpleadoSucursalSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@empleado_sucursal_bp.route('/', methods=['POST'])
def create_empleado_sucursal():
    try:
        data = request.get_json() or {}
        errors = EmpleadoSucursalSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 400

        empleado = Empleado.query.filter(
            Empleado.oid == data['fkEmpleado'],
            Empleado.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        if not empleado:
            return jsonify({'errors': ['El empleado no existe']}), 400

        existing = EmpleadoSucursal.query.filter(
            EmpleadoSucursal.fkEmpleado == data['fkEmpleado'],
            EmpleadoSucursal.fkSucursal == data['fkSucursal'],
            EmpleadoSucursal.estatus != BaseObjectEstatus.ELIMINADO,
        ).first()
        if existing:
            return jsonify({'errors': ['La asignación ya existe']}), 400

        item = EmpleadoSucursal(
            fkEmpleado=data['fkEmpleado'],
            fkSucursal=data['fkSucursal'],
            creado_por=data.get('creado_por'),
            estatus=BaseObjectEstatus.ACTIVO,
        )
        db.session.add(item)
        db.session.commit()
        return jsonify(EmpleadoSucursalSchema.serialize(item)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@empleado_sucursal_bp.route('/many', methods=['POST'])
def create_many_empleado_sucursales():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de asignaciones']}), 400

        created = []
        errors = []
        for idx, item in enumerate(data):
            validation_errors = EmpleadoSucursalSchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            existing = EmpleadoSucursal.query.filter(
                EmpleadoSucursal.fkEmpleado == item['fkEmpleado'],
                EmpleadoSucursal.fkSucursal == item['fkSucursal'],
                EmpleadoSucursal.estatus != BaseObjectEstatus.ELIMINADO,
            ).first()
            if existing:
                errors.append({'index': idx, 'errors': ['La asignación ya existe']})
                continue
            entity = EmpleadoSucursal(
                fkEmpleado=item['fkEmpleado'],
                fkSucursal=item['fkSucursal'],
                creado_por=item.get('creado_por'),
                estatus=BaseObjectEstatus.ACTIVO,
            )
            db.session.add(entity)
            created.append(entity)

        if created:
            db.session.commit()

        response = {'created': len(created), 'data': EmpleadoSucursalSchema.serialize_list(created)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@empleado_sucursal_bp.route('/<string:oid>', methods=['PUT'])
def update_empleado_sucursal(oid):
    try:
        item = EmpleadoSucursal.query.filter(
            EmpleadoSucursal.oid == oid,
            EmpleadoSucursal.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        if not item:
            return jsonify({'errors': ['Asignación no encontrada']}), 404

        data = request.get_json() or {}
        if 'editado_por' in data:
            item.editado_por = data['editado_por']
        item.updatedAt = datetime.utcnow()
        db.session.commit()
        return jsonify(EmpleadoSucursalSchema.serialize(item)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@empleado_sucursal_bp.route('/many', methods=['PUT'])
def update_many_empleado_sucursales():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de asignaciones']}), 400

        updated = []
        errors = []
        for idx, item in enumerate(data):
            if 'oid' not in item:
                errors.append({'index': idx, 'errors': ['oid es requerido']})
                continue
            entity = EmpleadoSucursal.query.filter(
                EmpleadoSucursal.oid == item['oid'],
                EmpleadoSucursal.estatus != BaseObjectEstatus.ELIMINADO
            ).first()
            if not entity:
                errors.append({'index': idx, 'errors': ['Asignación no encontrada']})
                continue
            if 'editado_por' in item:
                entity.editado_por = item['editado_por']
            entity.updatedAt = datetime.utcnow()
            updated.append(entity)

        if updated:
            db.session.commit()

        response = {'updated': len(updated), 'data': EmpleadoSucursalSchema.serialize_list(updated)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@empleado_sucursal_bp.route('/<string:oid>', methods=['DELETE'])
def delete_empleado_sucursal(oid):
    try:
        item = EmpleadoSucursal.query.filter(
            EmpleadoSucursal.oid == oid,
            EmpleadoSucursal.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        if not item:
            return jsonify({'errors': ['Asignación no encontrada']}), 404

        data = request.get_json() or {}
        item.estatus = BaseObjectEstatus.ELIMINADO
        item.editado_por = data.get('editado_por')
        item.updatedAt = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Asignación eliminada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@empleado_sucursal_bp.route('/list', methods=['POST'])
def get_empleado_sucursal_list():
    try:
        data = request.get_json()
        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400
        oid_list = data.get('oid_list', [])
        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400
        items = EmpleadoSucursal.query.filter(
            EmpleadoSucursal.oid.in_(oid_list),
            EmpleadoSucursal.estatus != BaseObjectEstatus.ELIMINADO
        ).all()
        return jsonify(EmpleadoSucursalSchema.serialize_list(items)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
