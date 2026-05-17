from flask import Blueprint, request, jsonify
from app import db
from app.models.corte_caja import CorteCaja
from app.models.turno_sucursal import TurnoSucursal
from app.schemas.corte_caja_schema import CorteCajaSchema
from app.enums import BaseObjectEstatus
from datetime import datetime

corte_caja_bp = Blueprint('corte_caja', __name__, url_prefix='/corte_caja')


@corte_caja_bp.route('/<string:oid>', methods=['GET'])
def get_corte_caja(oid):
    """Obtiene un corte de caja por su OID"""
    try:
        corte = CorteCaja.query.filter(
            CorteCaja.oid == oid,
            CorteCaja.estatus != BaseObjectEstatus.ELIMINADO
        ).first()

        if not corte:
            return jsonify({'errors': ['Corte de caja no encontrado']}), 404

        return jsonify(CorteCajaSchema.serialize(corte)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@corte_caja_bp.route('/', methods=['GET'])
def get_cortes_caja():
    """Obtiene listado de cortes de caja con paginación y filtros"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        fk_empresa = request.args.get('fkEmpresa', type=str)
        fk_sucursal = request.args.get('fkSucursal', type=str)
        fk_usuario = request.args.get('fkUsuario', type=str)
        fk_turno = request.args.get('fkTurno', type=str)
        fecha_inicio = request.args.get('fecha_inicio', type=str)
        fecha_fin = request.args.get('fecha_fin', type=str)

        query = CorteCaja.query.filter(CorteCaja.estatus != BaseObjectEstatus.ELIMINADO)

        if fk_empresa:
            query = query.filter(CorteCaja.fkEmpresa == fk_empresa)
        if fk_sucursal:
            query = query.filter(CorteCaja.fkSucursal == fk_sucursal)
        if fk_usuario:
            query = query.filter(CorteCaja.fkUsuario == fk_usuario)
        if fk_turno:
            query = query.filter(CorteCaja.fkTurno == fk_turno)
        if fecha_inicio:
            query = query.filter(CorteCaja.fecha >= datetime.strptime(fecha_inicio, '%Y-%m-%d'))
        if fecha_fin:
            query = query.filter(CorteCaja.fecha <= datetime.strptime(fecha_fin, '%Y-%m-%d'))

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'data': CorteCajaSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@corte_caja_bp.route('/', methods=['POST'])
def create_corte_caja():
    """Crea un nuevo corte de caja"""
    try:
        data = request.get_json()

        errors = CorteCajaSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 400

        # Verificar que el turno exista
        turno = TurnoSucursal.query.filter(
            TurnoSucursal.oid == data['fkTurno'],
            TurnoSucursal.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        if not turno:
            return jsonify({'errors': ['El turno especificado no existe']}), 400

        corte = CorteCaja(
            fecha=datetime.fromisoformat(data['fecha']),
            monto_inicial=data['monto_inicial'],
            monto_final=data['monto_final'],
            esperado=data['esperado'],
            diferencia=data['diferencia'],
            fkEmpresa=data['fkEmpresa'],
            fkSucursal=data['fkSucursal'],
            fkUsuario=data['fkUsuario'],
            fkTurno=data['fkTurno'],
            fkSistema=data['fkSistema'],
            creado_por=data.get('creado_por'),
            estatus=BaseObjectEstatus.ACTIVO
        )

        db.session.add(corte)
        db.session.commit()

        return jsonify(CorteCajaSchema.serialize(corte)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@corte_caja_bp.route('/many', methods=['POST'])
def create_many_cortes_caja():
    """Crea múltiples cortes de caja"""
    try:
        data = request.get_json()

        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de cortes de caja']}), 400

        cortes_created = []
        errors = []

        for idx, item in enumerate(data):
            validation_errors = CorteCajaSchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue

            turno = TurnoSucursal.query.filter(
                TurnoSucursal.oid == item['fkTurno'],
                TurnoSucursal.estatus != BaseObjectEstatus.ELIMINADO
            ).first()
            if not turno:
                errors.append({'index': idx, 'errors': ['El turno especificado no existe']})
                continue

            try:
                fecha = datetime.fromisoformat(item['fecha'])
            except ValueError:
                errors.append({'index': idx, 'errors': ['fecha tiene un formato inválido (use ISO 8601)']})
                continue

            corte = CorteCaja(
                fecha=fecha,
                monto_inicial=item['monto_inicial'],
                monto_final=item['monto_final'],
                esperado=item['esperado'],
                diferencia=item['diferencia'],
                fkEmpresa=item['fkEmpresa'],
                fkSucursal=item['fkSucursal'],
                fkUsuario=item['fkUsuario'],
                fkTurno=item['fkTurno'],
                fkSistema=item['fkSistema'],
                creado_por=item.get('creado_por'),
                estatus=BaseObjectEstatus.ACTIVO
            )

            db.session.add(corte)
            cortes_created.append(corte)

        if cortes_created:
            db.session.commit()

        response = {
            'created': len(cortes_created),
            'data': CorteCajaSchema.serialize_list(cortes_created)
        }

        if errors:
            response['errors'] = errors

        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@corte_caja_bp.route('/<string:oid>', methods=['PUT'])
def update_corte_caja(oid):
    """Actualiza un corte de caja"""
    try:
        corte = CorteCaja.query.filter(
            CorteCaja.oid == oid,
            CorteCaja.estatus != BaseObjectEstatus.ELIMINADO
        ).first()

        if not corte:
            return jsonify({'errors': ['Corte de caja no encontrado']}), 404

        data = request.get_json()

        errors = CorteCajaSchema.validate_update(data)
        if errors:
            return jsonify({'errors': errors}), 400

        if 'fecha' in data:
            corte.fecha = datetime.fromisoformat(data['fecha'])
        if 'monto_inicial' in data:
            corte.monto_inicial = data['monto_inicial']
        if 'monto_final' in data:
            corte.monto_final = data['monto_final']
        if 'esperado' in data:
            corte.esperado = data['esperado']
        if 'diferencia' in data:
            corte.diferencia = data['diferencia']
        if 'fkTurno' in data:
            turno = TurnoSucursal.query.filter(
                TurnoSucursal.oid == data['fkTurno'],
                TurnoSucursal.estatus != BaseObjectEstatus.ELIMINADO
            ).first()
            if not turno:
                return jsonify({'errors': ['El turno especificado no existe']}), 400
            corte.fkTurno = data['fkTurno']
        if 'fkEmpresa' in data:
            corte.fkEmpresa = data['fkEmpresa']
        if 'fkSucursal' in data:
            corte.fkSucursal = data['fkSucursal']
        if 'fkUsuario' in data:
            corte.fkUsuario = data['fkUsuario']
        if 'fkSistema' in data:
            corte.fkSistema = data['fkSistema']
        if 'editado_por' in data:
            corte.editado_por = data['editado_por']

        corte.updatedAt = datetime.utcnow()

        db.session.commit()

        return jsonify(CorteCajaSchema.serialize(corte)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@corte_caja_bp.route('/many', methods=['PUT'])
def update_many_cortes_caja():
    """Actualiza múltiples cortes de caja"""
    try:
        data = request.get_json()

        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de cortes de caja']}), 400

        cortes_updated = []
        errors = []

        for idx, item in enumerate(data):
            if 'oid' not in item:
                errors.append({'index': idx, 'errors': ['oid es requerido']})
                continue

            corte = CorteCaja.query.filter(
                CorteCaja.oid == item['oid'],
                CorteCaja.estatus != BaseObjectEstatus.ELIMINADO
            ).first()

            if not corte:
                errors.append({'index': idx, 'errors': ['Corte de caja no encontrado']})
                continue

            validation_errors = CorteCajaSchema.validate_update(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue

            if 'monto_inicial' in item:
                corte.monto_inicial = item['monto_inicial']
            if 'monto_final' in item:
                corte.monto_final = item['monto_final']
            if 'esperado' in item:
                corte.esperado = item['esperado']
            if 'diferencia' in item:
                corte.diferencia = item['diferencia']
            if 'editado_por' in item:
                corte.editado_por = item['editado_por']

            corte.updatedAt = datetime.utcnow()
            cortes_updated.append(corte)

        if cortes_updated:
            db.session.commit()

        response = {
            'updated': len(cortes_updated),
            'data': CorteCajaSchema.serialize_list(cortes_updated)
        }

        if errors:
            response['errors'] = errors

        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@corte_caja_bp.route('/<string:oid>', methods=['DELETE'])
def delete_corte_caja(oid):
    """Elimina (soft delete) un corte de caja"""
    try:
        corte = CorteCaja.query.filter(
            CorteCaja.oid == oid,
            CorteCaja.estatus != BaseObjectEstatus.ELIMINADO
        ).first()

        if not corte:
            return jsonify({'errors': ['Corte de caja no encontrado']}), 404

        data = request.get_json() or {}

        corte.estatus = BaseObjectEstatus.ELIMINADO
        corte.editado_por = data.get('editado_por')
        corte.updatedAt = datetime.utcnow()

        db.session.commit()

        return jsonify({'message': 'Corte de caja eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@corte_caja_bp.route('/list', methods=['POST'])
def get_corte_caja_list():
    """Obtiene una lista específica de cortes de caja a partir de un arreglo de OIDs"""
    try:
        data = request.get_json()

        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400

        oid_list = data.get('oid_list', [])

        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400

        cortes = CorteCaja.query.filter(
            CorteCaja.oid.in_(oid_list),
            CorteCaja.estatus != BaseObjectEstatus.ELIMINADO
        ).all()

        return jsonify(CorteCajaSchema.serialize_list(cortes)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
