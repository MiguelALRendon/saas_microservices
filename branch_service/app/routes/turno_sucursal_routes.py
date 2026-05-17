from flask import Blueprint, request, jsonify
from app import db
from app.models.turno_sucursal import TurnoSucursal
from app.schemas.turno_sucursal_schema import TurnoSucursalSchema
from app.enums import BaseObjectEstatus
from datetime import datetime

turno_sucursal_bp = Blueprint('turno_sucursal', __name__, url_prefix='/turno_sucursal')


@turno_sucursal_bp.route('/<string:oid>', methods=['GET'])
def get_turno_sucursal(oid):
    """Obtiene un turno de sucursal por su OID"""
    try:
        turno = TurnoSucursal.query.filter(
            TurnoSucursal.oid == oid,
            TurnoSucursal.estatus != BaseObjectEstatus.ELIMINADO
        ).first()

        if not turno:
            return jsonify({'errors': ['Turno de sucursal no encontrado']}), 404

        return jsonify(TurnoSucursalSchema.serialize(turno)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@turno_sucursal_bp.route('/', methods=['GET'])
def get_turnos_sucursal():
    """Obtiene listado de turnos de sucursal con paginación y filtros"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        nombre = request.args.get('nombre', type=str)
        fk_empresa = request.args.get('fkEmpresa', type=str)
        fk_sucursal = request.args.get('fkSucursal', type=str)

        query = TurnoSucursal.query.filter(TurnoSucursal.estatus != BaseObjectEstatus.ELIMINADO)

        if nombre:
            query = query.filter(TurnoSucursal.nombre.ilike(f'%{nombre}%'))
        if fk_empresa:
            query = query.filter(TurnoSucursal.fkEmpresa == fk_empresa)
        if fk_sucursal:
            query = query.filter(TurnoSucursal.fkSucursal == fk_sucursal)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'data': TurnoSucursalSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@turno_sucursal_bp.route('/', methods=['POST'])
def create_turno_sucursal():
    """Crea un nuevo turno de sucursal"""
    try:
        data = request.get_json()

        errors = TurnoSucursalSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 400

        turno = TurnoSucursal(
            nombre=data['nombre'],
            hora_entrada=datetime.strptime(data['hora_entrada'], '%H:%M:%S').time(),
            hora_salida=datetime.strptime(data['hora_salida'], '%H:%M:%S').time(),
            hora_corte=datetime.strptime(data['hora_corte'], '%H:%M:%S').time(),
            fkEmpresa=data['fkEmpresa'],
            fkSucursal=data['fkSucursal'],
            creado_por=data.get('creado_por'),
            estatus=BaseObjectEstatus.ACTIVO
        )

        db.session.add(turno)
        db.session.commit()

        return jsonify(TurnoSucursalSchema.serialize(turno)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@turno_sucursal_bp.route('/many', methods=['POST'])
def create_many_turnos_sucursal():
    """Crea múltiples turnos de sucursal"""
    try:
        data = request.get_json()

        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de turnos']}), 400

        turnos_created = []
        errors = []

        for idx, item in enumerate(data):
            validation_errors = TurnoSucursalSchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue

            try:
                turno = TurnoSucursal(
                    nombre=item['nombre'],
                    hora_entrada=datetime.strptime(item['hora_entrada'], '%H:%M:%S').time(),
                    hora_salida=datetime.strptime(item['hora_salida'], '%H:%M:%S').time(),
                    hora_corte=datetime.strptime(item['hora_corte'], '%H:%M:%S').time(),
                    fkEmpresa=item['fkEmpresa'],
                    fkSucursal=item['fkSucursal'],
                    creado_por=item.get('creado_por'),
                    estatus=BaseObjectEstatus.ACTIVO
                )
                db.session.add(turno)
                turnos_created.append(turno)
            except ValueError:
                errors.append({'index': idx, 'errors': ['Formato de hora inválido (use HH:MM:SS)']})
                continue

        if turnos_created:
            db.session.commit()

        response = {
            'created': len(turnos_created),
            'data': TurnoSucursalSchema.serialize_list(turnos_created)
        }

        if errors:
            response['errors'] = errors

        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@turno_sucursal_bp.route('/<string:oid>', methods=['PUT'])
def update_turno_sucursal(oid):
    """Actualiza un turno de sucursal"""
    try:
        turno = TurnoSucursal.query.filter(
            TurnoSucursal.oid == oid,
            TurnoSucursal.estatus != BaseObjectEstatus.ELIMINADO
        ).first()

        if not turno:
            return jsonify({'errors': ['Turno de sucursal no encontrado']}), 404

        data = request.get_json()

        errors = TurnoSucursalSchema.validate_update(data)
        if errors:
            return jsonify({'errors': errors}), 400

        if 'nombre' in data:
            turno.nombre = data['nombre']
        if 'hora_entrada' in data:
            turno.hora_entrada = datetime.strptime(data['hora_entrada'], '%H:%M:%S').time()
        if 'hora_salida' in data:
            turno.hora_salida = datetime.strptime(data['hora_salida'], '%H:%M:%S').time()
        if 'hora_corte' in data:
            turno.hora_corte = datetime.strptime(data['hora_corte'], '%H:%M:%S').time()
        if 'fkEmpresa' in data:
            turno.fkEmpresa = data['fkEmpresa']
        if 'fkSucursal' in data:
            turno.fkSucursal = data['fkSucursal']
        if 'editado_por' in data:
            turno.editado_por = data['editado_por']

        turno.updatedAt = datetime.utcnow()

        db.session.commit()

        return jsonify(TurnoSucursalSchema.serialize(turno)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@turno_sucursal_bp.route('/many', methods=['PUT'])
def update_many_turnos_sucursal():
    """Actualiza múltiples turnos de sucursal"""
    try:
        data = request.get_json()

        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de turnos']}), 400

        turnos_updated = []
        errors = []

        for idx, item in enumerate(data):
            if 'oid' not in item:
                errors.append({'index': idx, 'errors': ['oid es requerido']})
                continue

            turno = TurnoSucursal.query.filter(
                TurnoSucursal.oid == item['oid'],
                TurnoSucursal.estatus != BaseObjectEstatus.ELIMINADO
            ).first()

            if not turno:
                errors.append({'index': idx, 'errors': ['Turno de sucursal no encontrado']})
                continue

            validation_errors = TurnoSucursalSchema.validate_update(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue

            if 'nombre' in item:
                turno.nombre = item['nombre']
            if 'hora_entrada' in item:
                turno.hora_entrada = datetime.strptime(item['hora_entrada'], '%H:%M:%S').time()
            if 'hora_salida' in item:
                turno.hora_salida = datetime.strptime(item['hora_salida'], '%H:%M:%S').time()
            if 'hora_corte' in item:
                turno.hora_corte = datetime.strptime(item['hora_corte'], '%H:%M:%S').time()
            if 'editado_por' in item:
                turno.editado_por = item['editado_por']

            turno.updatedAt = datetime.utcnow()
            turnos_updated.append(turno)

        if turnos_updated:
            db.session.commit()

        response = {
            'updated': len(turnos_updated),
            'data': TurnoSucursalSchema.serialize_list(turnos_updated)
        }

        if errors:
            response['errors'] = errors

        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@turno_sucursal_bp.route('/<string:oid>', methods=['DELETE'])
def delete_turno_sucursal(oid):
    """Elimina (soft delete) un turno de sucursal"""
    try:
        turno = TurnoSucursal.query.filter(
            TurnoSucursal.oid == oid,
            TurnoSucursal.estatus != BaseObjectEstatus.ELIMINADO
        ).first()

        if not turno:
            return jsonify({'errors': ['Turno de sucursal no encontrado']}), 404

        data = request.get_json() or {}

        turno.estatus = BaseObjectEstatus.ELIMINADO
        turno.editado_por = data.get('editado_por')
        turno.updatedAt = datetime.utcnow()

        db.session.commit()

        return jsonify({'message': 'Turno de sucursal eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@turno_sucursal_bp.route('/list', methods=['POST'])
def get_turno_sucursal_list():
    """Obtiene una lista específica de turnos a partir de un arreglo de OIDs"""
    try:
        data = request.get_json()

        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400

        oid_list = data.get('oid_list', [])

        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400

        turnos = TurnoSucursal.query.filter(
            TurnoSucursal.oid.in_(oid_list),
            TurnoSucursal.estatus != BaseObjectEstatus.ELIMINADO
        ).all()

        return jsonify(TurnoSucursalSchema.serialize_list(turnos)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
