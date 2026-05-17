from datetime import datetime
from flask import Blueprint, request, jsonify
from app import db
from app.models.personaje_ficticio import PersonajeFicticio
from app.schemas.personaje_ficticio_schema import PersonajeFicticioSchema
from app.utils import generate_unique_url_busqueda

personaje_ficticio_bp = Blueprint('personaje_ficticio', __name__, url_prefix='/personaje-ficticio')


@personaje_ficticio_bp.route('/<string:oid>', methods=['GET'])
def get_personaje(oid):
    try:
        personaje = PersonajeFicticio.query.filter(
            PersonajeFicticio.id == oid, PersonajeFicticio.estatus == 1
        ).first()
        if not personaje:
            return jsonify({'errors': ['Personaje no encontrado']}), 404
        return jsonify(PersonajeFicticioSchema.serialize(personaje)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@personaje_ficticio_bp.route('/', methods=['GET'])
def get_personajes():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        nombre = request.args.get('nombre', type=str)

        query = PersonajeFicticio.query.filter(PersonajeFicticio.estatus == 1)
        if nombre:
            query = query.filter(PersonajeFicticio.nombre.ilike(f'%{nombre}%'))

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'data': PersonajeFicticioSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@personaje_ficticio_bp.route('/', methods=['POST'])
def create_personaje():
    try:
        data = request.get_json()
        errors = PersonajeFicticioSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 400

        url_busqueda = data.get('url_busqueda') or generate_unique_url_busqueda(data['nombre'], PersonajeFicticio)
        personaje = PersonajeFicticio(
            nombre=data['nombre'],
            url_foto_perfil=data.get('url_foto_perfil'),
            descripcion=data.get('descripcion'),
            url_busqueda=url_busqueda,
            estatus=1,
        )
        db.session.add(personaje)
        db.session.commit()
        return jsonify(PersonajeFicticioSchema.serialize(personaje)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@personaje_ficticio_bp.route('/many', methods=['POST'])
def create_many_personajes():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de personajes']}), 400

        created, errors = [], []
        for idx, item in enumerate(data):
            validation_errors = PersonajeFicticioSchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            url_busqueda = item.get('url_busqueda') or generate_unique_url_busqueda(item['nombre'], PersonajeFicticio)
            personaje = PersonajeFicticio(
                nombre=item['nombre'],
                url_foto_perfil=item.get('url_foto_perfil'),
                descripcion=item.get('descripcion'),
                url_busqueda=url_busqueda,
                estatus=1,
            )
            db.session.add(personaje)
            created.append(personaje)

        if created:
            db.session.commit()
        response = {'created': len(created), 'data': PersonajeFicticioSchema.serialize_list(created)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@personaje_ficticio_bp.route('/<string:oid>', methods=['PUT'])
def update_personaje(oid):
    try:
        personaje = PersonajeFicticio.query.filter(
            PersonajeFicticio.id == oid, PersonajeFicticio.estatus == 1
        ).first()
        if not personaje:
            return jsonify({'errors': ['Personaje no encontrado']}), 404

        data = request.get_json()
        if 'nombre' in data:
            personaje.nombre = data['nombre']
        if 'url_foto_perfil' in data:
            personaje.url_foto_perfil = data['url_foto_perfil']
        if 'descripcion' in data:
            personaje.descripcion = data['descripcion']
        if 'url_busqueda' in data:
            personaje.url_busqueda = data['url_busqueda']

        personaje.updated_at = datetime.now()
        db.session.commit()
        return jsonify(PersonajeFicticioSchema.serialize(personaje)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@personaje_ficticio_bp.route('/many', methods=['PUT'])
def update_many_personajes():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de personajes']}), 400

        updated, errors = [], []
        for idx, item in enumerate(data):
            if 'id' not in item:
                errors.append({'index': idx, 'errors': ['id es requerido']})
                continue
            personaje = PersonajeFicticio.query.filter(
                PersonajeFicticio.id == item['id'], PersonajeFicticio.estatus == 1
            ).first()
            if not personaje:
                errors.append({'index': idx, 'errors': ['Personaje no encontrado']})
                continue
            for field in ['nombre', 'url_foto_perfil', 'descripcion']:
                if field in item:
                    setattr(personaje, field, item[field])
            personaje.updated_at = datetime.now()
            updated.append(personaje)

        if updated:
            db.session.commit()
        response = {'updated': len(updated), 'data': PersonajeFicticioSchema.serialize_list(updated)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@personaje_ficticio_bp.route('/<string:oid>', methods=['DELETE'])
def delete_personaje(oid):
    try:
        personaje = PersonajeFicticio.query.filter(
            PersonajeFicticio.id == oid, PersonajeFicticio.estatus == 1
        ).first()
        if not personaje:
            return jsonify({'errors': ['Personaje no encontrado']}), 404
        personaje.estatus = -1
        personaje.updated_at = datetime.now()
        db.session.commit()
        return jsonify({'message': 'Personaje desactivado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@personaje_ficticio_bp.route('/list', methods=['POST'])
def get_personaje_list():
    try:
        data = request.get_json()
        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400
        oid_list = data.get('oid_list', [])
        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400
        personajes = PersonajeFicticio.query.filter(
            PersonajeFicticio.id.in_(oid_list), PersonajeFicticio.estatus == 1
        ).all()
        return jsonify(PersonajeFicticioSchema.serialize_list(personajes)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
