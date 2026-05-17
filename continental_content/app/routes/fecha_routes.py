from datetime import datetime, date as date_type
from flask import Blueprint, request, jsonify
from app import db
from app.models.fecha import Fecha
from app.schemas.fecha_schema import FechaSchema

fecha_bp = Blueprint('fecha', __name__, url_prefix='/fecha')


@fecha_bp.route('/<string:oid>', methods=['GET'])
def get_fecha(oid):
    try:
        fecha = Fecha.query.filter(Fecha.id == oid).first()
        if not fecha:
            return jsonify({'errors': ['Fecha no encontrada']}), 404
        return jsonify(FechaSchema.serialize(fecha)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@fecha_bp.route('/', methods=['GET'])
def get_fechas():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        query = Fecha.query.order_by(Fecha.fecha.asc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'data': FechaSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@fecha_bp.route('/', methods=['POST'])
def create_fecha():
    try:
        data = request.get_json()
        errors = FechaSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 400

        try:
            fecha_val = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'errors': ['fecha debe tener formato YYYY-MM-DD']}), 400

        fecha = Fecha(fecha=fecha_val, evento=data['evento'])
        db.session.add(fecha)
        db.session.commit()
        return jsonify(FechaSchema.serialize(fecha)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@fecha_bp.route('/many', methods=['POST'])
def create_many_fechas():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de fechas']}), 400

        created, errors = [], []
        for idx, item in enumerate(data):
            validation_errors = FechaSchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            try:
                fecha_val = datetime.strptime(item['fecha'], '%Y-%m-%d').date()
            except ValueError:
                errors.append({'index': idx, 'errors': ['fecha debe tener formato YYYY-MM-DD']})
                continue
            fecha = Fecha(fecha=fecha_val, evento=item['evento'])
            db.session.add(fecha)
            created.append(fecha)

        if created:
            db.session.commit()
        response = {'created': len(created), 'data': FechaSchema.serialize_list(created)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@fecha_bp.route('/<string:oid>', methods=['PUT'])
def update_fecha(oid):
    try:
        fecha = Fecha.query.filter(Fecha.id == oid).first()
        if not fecha:
            return jsonify({'errors': ['Fecha no encontrada']}), 404

        data = request.get_json()
        if 'fecha' in data:
            try:
                fecha.fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'errors': ['fecha debe tener formato YYYY-MM-DD']}), 400
        if 'evento' in data:
            fecha.evento = data['evento']

        fecha.updated_at = datetime.now()
        db.session.commit()
        return jsonify(FechaSchema.serialize(fecha)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@fecha_bp.route('/many', methods=['PUT'])
def update_many_fechas():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de fechas']}), 400

        updated, errors = [], []
        for idx, item in enumerate(data):
            if 'id' not in item:
                errors.append({'index': idx, 'errors': ['id es requerido']})
                continue
            fecha = Fecha.query.filter(Fecha.id == item['id']).first()
            if not fecha:
                errors.append({'index': idx, 'errors': ['Fecha no encontrada']})
                continue
            if 'fecha' in item:
                try:
                    fecha.fecha = datetime.strptime(item['fecha'], '%Y-%m-%d').date()
                except ValueError:
                    errors.append({'index': idx, 'errors': ['fecha debe tener formato YYYY-MM-DD']})
                    continue
            if 'evento' in item:
                fecha.evento = item['evento']
            fecha.updated_at = datetime.now()
            updated.append(fecha)

        if updated:
            db.session.commit()
        response = {'updated': len(updated), 'data': FechaSchema.serialize_list(updated)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@fecha_bp.route('/<string:oid>', methods=['DELETE'])
def delete_fecha(oid):
    """Hard delete — Fecha usa ConceptBase (sin estatus)."""
    try:
        fecha = Fecha.query.filter(Fecha.id == oid).first()
        if not fecha:
            return jsonify({'errors': ['Fecha no encontrada']}), 404
        db.session.delete(fecha)
        db.session.commit()
        return jsonify({'message': 'Fecha eliminada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@fecha_bp.route('/list', methods=['POST'])
def get_fecha_list():
    try:
        data = request.get_json()
        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400
        oid_list = data.get('oid_list', [])
        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400
        fechas = Fecha.query.filter(Fecha.id.in_(oid_list)).all()
        return jsonify(FechaSchema.serialize_list(fechas)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
