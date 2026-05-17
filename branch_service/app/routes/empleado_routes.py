from flask import Blueprint, request, jsonify
from app import db
from app.models.empleado import Empleado
from app.models.cargo import Cargo
from app.schemas.empleado_schema import EmpleadoSchema
from app.enums import BaseObjectEstatus
from datetime import datetime, date

empleado_bp = Blueprint('empleado', __name__, url_prefix='/empleado')


@empleado_bp.route('/<string:oid>', methods=['GET'])
def get_empleado(oid):
    """Obtiene un empleado por su OID"""
    try:
        empleado = Empleado.query.filter(
            Empleado.oid == oid,
            Empleado.estatus != BaseObjectEstatus.ELIMINADO
        ).first()

        if not empleado:
            return jsonify({'errors': ['Empleado no encontrado']}), 404

        return jsonify(EmpleadoSchema.serialize(empleado)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@empleado_bp.route('/', methods=['GET'])
def get_empleados():
    """Obtiene listado de empleados con paginación y filtros"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        nombres = request.args.get('nombres', type=str)
        apellido_paterno = request.args.get('apellido_paterno', type=str)
        fk_empresa = request.args.get('fkEmpresa', type=str)
        fk_sucursal = request.args.get('fkSucursal', type=str)
        fk_cargo = request.args.get('fkCargo', type=str)

        query = Empleado.query.filter(Empleado.estatus != BaseObjectEstatus.ELIMINADO)

        if nombres:
            query = query.filter(Empleado.nombres.ilike(f'%{nombres}%'))
        if apellido_paterno:
            query = query.filter(Empleado.apellido_paterno.ilike(f'%{apellido_paterno}%'))
        if fk_empresa:
            query = query.filter(Empleado.fkEmpresa == fk_empresa)
        if fk_sucursal:
            query = query.filter(Empleado.fkSucursal == fk_sucursal)
        if fk_cargo:
            query = query.filter(Empleado.fkCargo == fk_cargo)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'data': EmpleadoSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@empleado_bp.route('/', methods=['POST'])
def create_empleado():
    """Crea un nuevo empleado"""
    try:
        data = request.get_json()

        errors = EmpleadoSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 400

        # Verificar que el cargo exista
        cargo = Cargo.query.filter(
            Cargo.oid == data['fkCargo'],
            Cargo.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        if not cargo:
            return jsonify({'errors': ['El cargo especificado no existe']}), 400

        # Verificar unicidad de CURP si se proporciona
        if data.get('curp') and Empleado.query.filter_by(curp=data['curp']).first():
            return jsonify({'errors': ['El CURP ya está registrado']}), 400

        fecha_contratacion = datetime.strptime(data['fecha_contratacion'], '%Y-%m-%d').date()

        empleado = Empleado(
            nombres=data['nombres'],
            apellido_paterno=data['apellido_paterno'],
            apellido_materno=data['apellido_materno'],
            curp=data.get('curp'),
            rfc=data.get('rfc'),
            fecha_contratacion=fecha_contratacion,
            telefono=data.get('telefono'),
            email=data.get('email'),
            fkCargo=data['fkCargo'],
            fkEmpresa=data['fkEmpresa'],
            fkSucursal=data['fkSucursal'],
            creado_por=data.get('creado_por'),
            estatus=BaseObjectEstatus.ACTIVO
        )

        db.session.add(empleado)
        db.session.commit()

        return jsonify(EmpleadoSchema.serialize(empleado)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@empleado_bp.route('/many', methods=['POST'])
def create_many_empleados():
    """Crea múltiples empleados"""
    try:
        data = request.get_json()

        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de empleados']}), 400

        empleados_created = []
        errors = []

        for idx, item in enumerate(data):
            validation_errors = EmpleadoSchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue

            cargo = Cargo.query.filter(
                Cargo.oid == item['fkCargo'],
                Cargo.estatus != BaseObjectEstatus.ELIMINADO
            ).first()
            if not cargo:
                errors.append({'index': idx, 'errors': ['El cargo especificado no existe']})
                continue

            if item.get('curp') and Empleado.query.filter_by(curp=item['curp']).first():
                errors.append({'index': idx, 'errors': ['El CURP ya está registrado']})
                continue

            try:
                fecha_contratacion = datetime.strptime(item['fecha_contratacion'], '%Y-%m-%d').date()
            except ValueError:
                errors.append({'index': idx, 'errors': ['fecha_contratacion tiene un formato inválido (use YYYY-MM-DD)']})
                continue

            empleado = Empleado(
                nombres=item['nombres'],
                apellido_paterno=item['apellido_paterno'],
                apellido_materno=item['apellido_materno'],
                curp=item.get('curp'),
                rfc=item.get('rfc'),
                fecha_contratacion=fecha_contratacion,
                telefono=item.get('telefono'),
                email=item.get('email'),
                fkCargo=item['fkCargo'],
                fkEmpresa=item['fkEmpresa'],
                fkSucursal=item['fkSucursal'],
                creado_por=item.get('creado_por'),
                estatus=BaseObjectEstatus.ACTIVO
            )

            db.session.add(empleado)
            empleados_created.append(empleado)

        if empleados_created:
            db.session.commit()

        response = {
            'created': len(empleados_created),
            'data': EmpleadoSchema.serialize_list(empleados_created)
        }

        if errors:
            response['errors'] = errors

        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@empleado_bp.route('/<string:oid>', methods=['PUT'])
def update_empleado(oid):
    """Actualiza un empleado"""
    try:
        empleado = Empleado.query.filter(
            Empleado.oid == oid,
            Empleado.estatus != BaseObjectEstatus.ELIMINADO
        ).first()

        if not empleado:
            return jsonify({'errors': ['Empleado no encontrado']}), 404

        data = request.get_json()

        errors = EmpleadoSchema.validate_update(data)
        if errors:
            return jsonify({'errors': errors}), 400

        if 'nombres' in data:
            empleado.nombres = data['nombres']
        if 'apellido_paterno' in data:
            empleado.apellido_paterno = data['apellido_paterno']
        if 'apellido_materno' in data:
            empleado.apellido_materno = data['apellido_materno']
        if 'curp' in data:
            if data['curp']:
                existing = Empleado.query.filter(
                    Empleado.curp == data['curp'],
                    Empleado.oid != oid
                ).first()
                if existing:
                    return jsonify({'errors': ['El CURP ya está registrado']}), 400
            empleado.curp = data['curp']
        if 'rfc' in data:
            empleado.rfc = data['rfc']
        if 'fecha_contratacion' in data:
            empleado.fecha_contratacion = datetime.strptime(data['fecha_contratacion'], '%Y-%m-%d').date()
        if 'telefono' in data:
            empleado.telefono = data['telefono']
        if 'email' in data:
            empleado.email = data['email']
        if 'fkCargo' in data:
            cargo = Cargo.query.filter(
                Cargo.oid == data['fkCargo'],
                Cargo.estatus != BaseObjectEstatus.ELIMINADO
            ).first()
            if not cargo:
                return jsonify({'errors': ['El cargo especificado no existe']}), 400
            empleado.fkCargo = data['fkCargo']
        if 'fkEmpresa' in data:
            empleado.fkEmpresa = data['fkEmpresa']
        if 'fkSucursal' in data:
            empleado.fkSucursal = data['fkSucursal']
        if 'editado_por' in data:
            empleado.editado_por = data['editado_por']

        empleado.updatedAt = datetime.utcnow()

        db.session.commit()

        return jsonify(EmpleadoSchema.serialize(empleado)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@empleado_bp.route('/many', methods=['PUT'])
def update_many_empleados():
    """Actualiza múltiples empleados"""
    try:
        data = request.get_json()

        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de empleados']}), 400

        empleados_updated = []
        errors = []

        for idx, item in enumerate(data):
            if 'oid' not in item:
                errors.append({'index': idx, 'errors': ['oid es requerido']})
                continue

            empleado = Empleado.query.filter(
                Empleado.oid == item['oid'],
                Empleado.estatus != BaseObjectEstatus.ELIMINADO
            ).first()

            if not empleado:
                errors.append({'index': idx, 'errors': ['Empleado no encontrado']})
                continue

            validation_errors = EmpleadoSchema.validate_update(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue

            if 'nombres' in item:
                empleado.nombres = item['nombres']
            if 'apellido_paterno' in item:
                empleado.apellido_paterno = item['apellido_paterno']
            if 'apellido_materno' in item:
                empleado.apellido_materno = item['apellido_materno']
            if 'rfc' in item:
                empleado.rfc = item['rfc']
            if 'telefono' in item:
                empleado.telefono = item['telefono']
            if 'email' in item:
                empleado.email = item['email']
            if 'editado_por' in item:
                empleado.editado_por = item['editado_por']

            empleado.updatedAt = datetime.utcnow()
            empleados_updated.append(empleado)

        if empleados_updated:
            db.session.commit()

        response = {
            'updated': len(empleados_updated),
            'data': EmpleadoSchema.serialize_list(empleados_updated)
        }

        if errors:
            response['errors'] = errors

        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@empleado_bp.route('/<string:oid>', methods=['DELETE'])
def delete_empleado(oid):
    """Elimina (soft delete) un empleado"""
    try:
        empleado = Empleado.query.filter(
            Empleado.oid == oid,
            Empleado.estatus != BaseObjectEstatus.ELIMINADO
        ).first()

        if not empleado:
            return jsonify({'errors': ['Empleado no encontrado']}), 404

        data = request.get_json() or {}

        empleado.estatus = BaseObjectEstatus.ELIMINADO
        empleado.editado_por = data.get('editado_por')
        empleado.updatedAt = datetime.utcnow()

        db.session.commit()

        return jsonify({'message': 'Empleado eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@empleado_bp.route('/list', methods=['POST'])
def get_empleado_list():
    """Obtiene una lista específica de empleados a partir de un arreglo de OIDs"""
    try:
        data = request.get_json()

        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400

        oid_list = data.get('oid_list', [])

        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400

        empleados = Empleado.query.filter(
            Empleado.oid.in_(oid_list),
            Empleado.estatus != BaseObjectEstatus.ELIMINADO
        ).all()

        return jsonify(EmpleadoSchema.serialize_list(empleados)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
