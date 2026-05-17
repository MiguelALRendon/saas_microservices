from datetime import datetime
from flask import Blueprint, request, jsonify
from app import db
from app.models.arco import Arco
from app.schemas.arco_schema import ArcoSchema
from app.utils import generate_unique_url_busqueda

arco_bp = Blueprint('arco', __name__, url_prefix='/arco')


@arco_bp.route('/<string:oid>', methods=['GET'])
def get_arco(oid):
    try:
        arco = Arco.query.filter(Arco.id == oid, Arco.estatus == 1).first()
        if not arco:
            return jsonify({'errors': ['Arco no encontrado']}), 404
        return jsonify(ArcoSchema.serialize(arco)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@arco_bp.route('/', methods=['GET'])
def get_arcos():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        nombre = request.args.get('nombre', type=str)
        es_subarco = request.args.get('es_subarco', type=str)

        query = Arco.query.filter(Arco.estatus == 1).order_by(Arco.orden.asc())
        if nombre:
            query = query.filter(Arco.nombre.ilike(f'%{nombre}%'))
        if es_subarco is not None:
            query = query.filter(Arco.es_subarco == (es_subarco.lower() == 'true'))

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'data': ArcoSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@arco_bp.route('/', methods=['POST'])
def create_arco():
    try:
        data = request.get_json()
        errors = ArcoSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 400

        url_busqueda = data.get('url_busqueda') or generate_unique_url_busqueda(data['nombre'], Arco)
        arco = Arco(
            nombre=data['nombre'],
            es_subarco=data.get('es_subarco', False),
            orden=data.get('orden'),
            url_busqueda=url_busqueda,
            estatus=1,
        )
        db.session.add(arco)
        db.session.commit()
        return jsonify(ArcoSchema.serialize(arco)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@arco_bp.route('/many', methods=['POST'])
def create_many_arcos():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de arcos']}), 400

        created, errors = [], []
        for idx, item in enumerate(data):
            validation_errors = ArcoSchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            url_busqueda = item.get('url_busqueda') or generate_unique_url_busqueda(item['nombre'], Arco)
            arco = Arco(
                nombre=item['nombre'],
                es_subarco=item.get('es_subarco', False),
                orden=item.get('orden'),
                url_busqueda=url_busqueda,
                estatus=1,
            )
            db.session.add(arco)
            created.append(arco)

        if created:
            db.session.commit()
        response = {'created': len(created), 'data': ArcoSchema.serialize_list(created)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@arco_bp.route('/<string:oid>', methods=['PUT'])
def update_arco(oid):
    try:
        arco = Arco.query.filter(Arco.id == oid, Arco.estatus == 1).first()
        if not arco:
            return jsonify({'errors': ['Arco no encontrado']}), 404

        data = request.get_json()
        if 'nombre' in data:
            arco.nombre = data['nombre']
        if 'es_subarco' in data:
            arco.es_subarco = data['es_subarco']
        if 'orden' in data:
            arco.orden = data['orden']
        if 'url_busqueda' in data:
            arco.url_busqueda = data['url_busqueda']

        arco.updated_at = datetime.now()
        db.session.commit()
        return jsonify(ArcoSchema.serialize(arco)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@arco_bp.route('/many', methods=['PUT'])
def update_many_arcos():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de arcos']}), 400

        updated, errors = [], []
        for idx, item in enumerate(data):
            if 'id' not in item:
                errors.append({'index': idx, 'errors': ['id es requerido']})
                continue
            arco = Arco.query.filter(Arco.id == item['id'], Arco.estatus == 1).first()
            if not arco:
                errors.append({'index': idx, 'errors': ['Arco no encontrado']})
                continue
            if 'nombre' in item:
                arco.nombre = item['nombre']
            if 'es_subarco' in item:
                arco.es_subarco = item['es_subarco']
            if 'orden' in item:
                arco.orden = item['orden']
            arco.updated_at = datetime.now()
            updated.append(arco)

        if updated:
            db.session.commit()
        response = {'updated': len(updated), 'data': ArcoSchema.serialize_list(updated)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@arco_bp.route('/<string:oid>', methods=['DELETE'])
def delete_arco(oid):
    try:
        arco = Arco.query.filter(Arco.id == oid, Arco.estatus == 1).first()
        if not arco:
            return jsonify({'errors': ['Arco no encontrado']}), 404
        arco.estatus = -1
        arco.updated_at = datetime.now()
        db.session.commit()
        return jsonify({'message': 'Arco desactivado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@arco_bp.route('/list', methods=['POST'])
def get_arco_list():
    try:
        data = request.get_json()
        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400
        oid_list = data.get('oid_list', [])
        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400
        arcos = Arco.query.filter(Arco.id.in_(oid_list), Arco.estatus == 1).all()
        return jsonify(ArcoSchema.serialize_list(arcos)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
