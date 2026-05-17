from datetime import datetime
from flask import Blueprint, request, jsonify
from app import db
from app.models.obra import Obra
from app.schemas.obra_schema import ObraSchema
from app.utils import generate_unique_url_busqueda

obra_bp = Blueprint('obra', __name__, url_prefix='/obra')


@obra_bp.route('/<string:oid>', methods=['GET'])
def get_obra(oid):
    try:
        obra = Obra.query.filter(Obra.id == oid, Obra.estatus == 1).first()
        if not obra:
            return jsonify({'errors': ['Obra no encontrada']}), 404
        return jsonify(ObraSchema.serialize(obra)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@obra_bp.route('/', methods=['GET'])
def get_obras():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        nombre = request.args.get('nombre', type=str)

        query = Obra.query.filter(Obra.estatus == 1).order_by(Obra.orden.asc())
        if nombre:
            query = query.filter(Obra.nombre.ilike(f'%{nombre}%'))

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'data': ObraSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@obra_bp.route('/', methods=['POST'])
def create_obra():
    try:
        data = request.get_json()
        errors = ObraSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 400

        url_busqueda = data.get('url_busqueda') or generate_unique_url_busqueda(data['nombre'], Obra)
        obra = Obra(
            nombre=data['nombre'],
            descripcion=data.get('descripcion'),
            url_portada=data.get('url_portada'),
            orden=data.get('orden'),
            icono=data.get('icono'),
            url_busqueda=url_busqueda,
            estatus=1,
        )
        db.session.add(obra)
        db.session.commit()
        return jsonify(ObraSchema.serialize(obra)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@obra_bp.route('/many', methods=['POST'])
def create_many_obras():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de obras']}), 400

        created, errors = [], []
        for idx, item in enumerate(data):
            validation_errors = ObraSchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            url_busqueda = item.get('url_busqueda') or generate_unique_url_busqueda(item['nombre'], Obra)
            obra = Obra(
                nombre=item['nombre'],
                descripcion=item.get('descripcion'),
                url_portada=item.get('url_portada'),
                orden=item.get('orden'),
                icono=item.get('icono'),
                url_busqueda=url_busqueda,
                estatus=1,
            )
            db.session.add(obra)
            created.append(obra)

        if created:
            db.session.commit()
        response = {'created': len(created), 'data': ObraSchema.serialize_list(created)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@obra_bp.route('/<string:oid>', methods=['PUT'])
def update_obra(oid):
    try:
        obra = Obra.query.filter(Obra.id == oid, Obra.estatus == 1).first()
        if not obra:
            return jsonify({'errors': ['Obra no encontrada']}), 404

        data = request.get_json()
        errors = ObraSchema.validate_update(data)
        if errors:
            return jsonify({'errors': errors}), 400

        if 'nombre' in data:
            obra.nombre = data['nombre']
        if 'descripcion' in data:
            obra.descripcion = data['descripcion']
        if 'url_portada' in data:
            obra.url_portada = data['url_portada']
        if 'orden' in data:
            obra.orden = data['orden']
        if 'icono' in data:
            obra.icono = data['icono']
        if 'url_busqueda' in data:
            obra.url_busqueda = data['url_busqueda']

        obra.updated_at = datetime.now()
        db.session.commit()
        return jsonify(ObraSchema.serialize(obra)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@obra_bp.route('/many', methods=['PUT'])
def update_many_obras():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de obras']}), 400

        updated, errors = [], []
        for idx, item in enumerate(data):
            if 'id' not in item:
                errors.append({'index': idx, 'errors': ['id es requerido']})
                continue
            obra = Obra.query.filter(Obra.id == item['id'], Obra.estatus == 1).first()
            if not obra:
                errors.append({'index': idx, 'errors': ['Obra no encontrada']})
                continue
            validation_errors = ObraSchema.validate_update(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            if 'nombre' in item:
                obra.nombre = item['nombre']
            if 'descripcion' in item:
                obra.descripcion = item['descripcion']
            if 'url_portada' in item:
                obra.url_portada = item['url_portada']
            if 'orden' in item:
                obra.orden = item['orden']
            if 'icono' in item:
                obra.icono = item['icono']
            obra.updated_at = datetime.now()
            updated.append(obra)

        if updated:
            db.session.commit()
        response = {'updated': len(updated), 'data': ObraSchema.serialize_list(updated)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@obra_bp.route('/<string:oid>', methods=['DELETE'])
def delete_obra(oid):
    try:
        obra = Obra.query.filter(Obra.id == oid, Obra.estatus == 1).first()
        if not obra:
            return jsonify({'errors': ['Obra no encontrada']}), 404
        obra.estatus = -1
        obra.updated_at = datetime.now()
        db.session.commit()
        return jsonify({'message': 'Obra desactivada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@obra_bp.route('/list', methods=['POST'])
def get_obra_list():
    try:
        data = request.get_json()
        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400
        oid_list = data.get('oid_list', [])
        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400
        obras = Obra.query.filter(Obra.id.in_(oid_list), Obra.estatus == 1).all()
        return jsonify(ObraSchema.serialize_list(obras)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
