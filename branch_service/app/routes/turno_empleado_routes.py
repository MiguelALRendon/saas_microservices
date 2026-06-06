from flask import Blueprint, request, jsonify
from app import db
from app.models.turno_empleado import TurnoEmpleado
from app.models.turno_sucursal import TurnoSucursal
from app.models.empleado import Empleado
from app.schemas.turno_empleado_schema import TurnoEmpleadoSchema
from app.enums import BaseObjectEstatus, DiaSemana
from datetime import datetime

turno_empleado_bp = Blueprint('turno_empleado', __name__, url_prefix='/turno-empleado')


def _parse_date(value):
    return datetime.strptime(value, '%Y-%m-%d').date()


@turno_empleado_bp.route('/<string:oid>', methods=['GET'])
def get_turno_empleado(oid):
    try:
        item = TurnoEmpleado.query.filter(
            TurnoEmpleado.oid == oid,
            TurnoEmpleado.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        if not item:
            return jsonify({'errors': ['Asignación no encontrada']}), 404
        return jsonify(TurnoEmpleadoSchema.serialize(item)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@turno_empleado_bp.route('/', methods=['GET'])
def get_turno_empleados():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        fk_turno = request.args.get('fkTurnoSucursal', type=str)
        fk_empleado = request.args.get('fkEmpleado', type=str)
        dia = request.args.get('diaSemana', type=str)

        query = TurnoEmpleado.query.filter(TurnoEmpleado.estatus != BaseObjectEstatus.ELIMINADO)
        if fk_turno:
            query = query.filter(TurnoEmpleado.fkTurnoSucursal == fk_turno)
        if fk_empleado:
            query = query.filter(TurnoEmpleado.fkEmpleado == fk_empleado)
        if dia:
            if dia not in DiaSemana.__members__:
                return jsonify({'errors': ['diaSemana inválido']}), 400
            query = query.filter(TurnoEmpleado.diaSemana == DiaSemana[dia])

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'data': TurnoEmpleadoSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@turno_empleado_bp.route('/', methods=['POST'])
def create_turno_empleado():
    try:
        data = request.get_json() or {}
        errors = TurnoEmpleadoSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 400

        turno = TurnoSucursal.query.filter(
            TurnoSucursal.oid == data['fkTurnoSucursal'],
            TurnoSucursal.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        if not turno:
            return jsonify({'errors': ['El turno especificado no existe']}), 400

        empleado = Empleado.query.filter(
            Empleado.oid == data['fkEmpleado'],
            Empleado.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        if not empleado:
            return jsonify({'errors': ['El empleado especificado no existe']}), 400

        try:
            fecha_inicio = _parse_date(data['fechaInicio'])
            fecha_fin = _parse_date(data['fechaFin']) if data.get('fechaFin') else None
        except ValueError:
            return jsonify({'errors': ['fechaInicio/fechaFin con formato inválido (use YYYY-MM-DD)']}), 400

        existing = TurnoEmpleado.query.filter(
            TurnoEmpleado.fkTurnoSucursal == data['fkTurnoSucursal'],
            TurnoEmpleado.fkEmpleado == data['fkEmpleado'],
            TurnoEmpleado.diaSemana == DiaSemana[data['diaSemana']],
            TurnoEmpleado.fechaInicio == fecha_inicio,
            TurnoEmpleado.estatus != BaseObjectEstatus.ELIMINADO,
        ).first()
        if existing:
            return jsonify({'errors': ['La asignación ya existe para esa fecha y día']}), 400

        item = TurnoEmpleado(
            fkTurnoSucursal=data['fkTurnoSucursal'],
            fkEmpleado=data['fkEmpleado'],
            diaSemana=DiaSemana[data['diaSemana']],
            fechaInicio=fecha_inicio,
            fechaFin=fecha_fin,
            creado_por=data.get('creado_por'),
            estatus=BaseObjectEstatus.ACTIVO,
        )
        db.session.add(item)
        db.session.commit()
        return jsonify(TurnoEmpleadoSchema.serialize(item)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@turno_empleado_bp.route('/many', methods=['POST'])
def create_many_turno_empleados():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de asignaciones']}), 400

        created = []
        errors = []
        for idx, item in enumerate(data):
            validation_errors = TurnoEmpleadoSchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            try:
                fecha_inicio = _parse_date(item['fechaInicio'])
                fecha_fin = _parse_date(item['fechaFin']) if item.get('fechaFin') else None
            except ValueError:
                errors.append({'index': idx, 'errors': ['fechaInicio/fechaFin con formato inválido (use YYYY-MM-DD)']})
                continue

            entity = TurnoEmpleado(
                fkTurnoSucursal=item['fkTurnoSucursal'],
                fkEmpleado=item['fkEmpleado'],
                diaSemana=DiaSemana[item['diaSemana']],
                fechaInicio=fecha_inicio,
                fechaFin=fecha_fin,
                creado_por=item.get('creado_por'),
                estatus=BaseObjectEstatus.ACTIVO,
            )
            db.session.add(entity)
            created.append(entity)

        if created:
            db.session.commit()

        response = {'created': len(created), 'data': TurnoEmpleadoSchema.serialize_list(created)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@turno_empleado_bp.route('/<string:oid>', methods=['PUT'])
def update_turno_empleado(oid):
    try:
        item = TurnoEmpleado.query.filter(
            TurnoEmpleado.oid == oid,
            TurnoEmpleado.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        if not item:
            return jsonify({'errors': ['Asignación no encontrada']}), 404

        data = request.get_json() or {}
        errors = TurnoEmpleadoSchema.validate_update(data)
        if errors:
            return jsonify({'errors': errors}), 400

        if 'diaSemana' in data:
            item.diaSemana = DiaSemana[data['diaSemana']]
        if 'fechaInicio' in data:
            try:
                item.fechaInicio = _parse_date(data['fechaInicio'])
            except ValueError:
                return jsonify({'errors': ['fechaInicio con formato inválido (use YYYY-MM-DD)']}), 400
        if 'fechaFin' in data:
            try:
                item.fechaFin = _parse_date(data['fechaFin']) if data['fechaFin'] else None
            except ValueError:
                return jsonify({'errors': ['fechaFin con formato inválido (use YYYY-MM-DD)']}), 400
        if 'editado_por' in data:
            item.editado_por = data['editado_por']
        item.updatedAt = datetime.utcnow()

        db.session.commit()
        return jsonify(TurnoEmpleadoSchema.serialize(item)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@turno_empleado_bp.route('/many', methods=['PUT'])
def update_many_turno_empleados():
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
            entity = TurnoEmpleado.query.filter(
                TurnoEmpleado.oid == item['oid'],
                TurnoEmpleado.estatus != BaseObjectEstatus.ELIMINADO
            ).first()
            if not entity:
                errors.append({'index': idx, 'errors': ['Asignación no encontrada']})
                continue
            validation_errors = TurnoEmpleadoSchema.validate_update(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue

            if 'diaSemana' in item:
                entity.diaSemana = DiaSemana[item['diaSemana']]
            if 'fechaInicio' in item:
                try:
                    entity.fechaInicio = _parse_date(item['fechaInicio'])
                except ValueError:
                    errors.append({'index': idx, 'errors': ['fechaInicio con formato inválido']})
                    continue
            if 'fechaFin' in item:
                try:
                    entity.fechaFin = _parse_date(item['fechaFin']) if item['fechaFin'] else None
                except ValueError:
                    errors.append({'index': idx, 'errors': ['fechaFin con formato inválido']})
                    continue
            if 'editado_por' in item:
                entity.editado_por = item['editado_por']
            entity.updatedAt = datetime.utcnow()
            updated.append(entity)

        if updated:
            db.session.commit()

        response = {'updated': len(updated), 'data': TurnoEmpleadoSchema.serialize_list(updated)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@turno_empleado_bp.route('/<string:oid>', methods=['DELETE'])
def delete_turno_empleado(oid):
    try:
        item = TurnoEmpleado.query.filter(
            TurnoEmpleado.oid == oid,
            TurnoEmpleado.estatus != BaseObjectEstatus.ELIMINADO
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


@turno_empleado_bp.route('/list', methods=['POST'])
def get_turno_empleado_list():
    try:
        data = request.get_json()
        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400
        oid_list = data.get('oid_list', [])
        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400
        items = TurnoEmpleado.query.filter(
            TurnoEmpleado.oid.in_(oid_list),
            TurnoEmpleado.estatus != BaseObjectEstatus.ELIMINADO
        ).all()
        return jsonify(TurnoEmpleadoSchema.serialize_list(items)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
