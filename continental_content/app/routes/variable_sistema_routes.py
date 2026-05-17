from datetime import datetime
from flask import Blueprint, request, jsonify
from app import db
from app.models.variable_sistema import VariableSistema
from app.schemas.variable_sistema_schema import VariableSistemaSchema
from app.utils import generate_unique_url_busqueda

variable_sistema_bp = Blueprint('variable_sistema', __name__, url_prefix='/variable-sistema')


@variable_sistema_bp.route('/<string:oid>', methods=['GET'])
def get_variable(oid):
    try:
        variable = VariableSistema.query.filter(
            VariableSistema.id == oid, VariableSistema.estatus == 1
        ).first()
        if not variable:
            return jsonify({'errors': ['Variable no encontrada']}), 404
        return jsonify(VariableSistemaSchema.serialize(variable)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@variable_sistema_bp.route('/', methods=['GET'])
def get_variables():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        nombre = request.args.get('nombre', type=str)

        query = VariableSistema.query.filter(VariableSistema.estatus == 1)
        if nombre:
            query = query.filter(VariableSistema.nombre.ilike(f'%{nombre}%'))

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'data': VariableSistemaSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@variable_sistema_bp.route('/', methods=['POST'])
def create_variable():
    try:
        data = request.get_json()
        errors = VariableSistemaSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 400

        if VariableSistema.query.filter_by(nombre=data['nombre']).first():
            return jsonify({'errors': ['Ya existe una variable con ese nombre']}), 400

        url_busqueda = data.get('url_busqueda') or generate_unique_url_busqueda(data['nombre'], VariableSistema)
        variable = VariableSistema(
            nombre=data['nombre'],
            valor=data.get('valor'),
            url_busqueda=url_busqueda,
            estatus=1,
        )
        db.session.add(variable)
        db.session.commit()
        return jsonify(VariableSistemaSchema.serialize(variable)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@variable_sistema_bp.route('/many', methods=['POST'])
def create_many_variables():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de variables']}), 400

        created, errors = [], []
        for idx, item in enumerate(data):
            validation_errors = VariableSistemaSchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            if VariableSistema.query.filter_by(nombre=item['nombre']).first():
                errors.append({'index': idx, 'errors': ['Ya existe una variable con ese nombre']})
                continue
            url_busqueda = item.get('url_busqueda') or generate_unique_url_busqueda(item['nombre'], VariableSistema)
            variable = VariableSistema(
                nombre=item['nombre'],
                valor=item.get('valor'),
                url_busqueda=url_busqueda,
                estatus=1,
            )
            db.session.add(variable)
            created.append(variable)

        if created:
            db.session.commit()
        response = {'created': len(created), 'data': VariableSistemaSchema.serialize_list(created)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@variable_sistema_bp.route('/<string:oid>', methods=['PUT'])
def update_variable(oid):
    try:
        variable = VariableSistema.query.filter(
            VariableSistema.id == oid, VariableSistema.estatus == 1
        ).first()
        if not variable:
            return jsonify({'errors': ['Variable no encontrada']}), 404

        data = request.get_json()
        if 'nombre' in data:
            existing = VariableSistema.query.filter(
                VariableSistema.nombre == data['nombre'],
                VariableSistema.id != oid
            ).first()
            if existing:
                return jsonify({'errors': ['Ya existe una variable con ese nombre']}), 400
            variable.nombre = data['nombre']
        if 'valor' in data:
            variable.valor = data['valor']
        if 'url_busqueda' in data:
            variable.url_busqueda = data['url_busqueda']

        variable.updated_at = datetime.now()
        db.session.commit()
        return jsonify(VariableSistemaSchema.serialize(variable)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@variable_sistema_bp.route('/many', methods=['PUT'])
def update_many_variables():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de variables']}), 400

        updated, errors = [], []
        for idx, item in enumerate(data):
            if 'id' not in item:
                errors.append({'index': idx, 'errors': ['id es requerido']})
                continue
            variable = VariableSistema.query.filter(
                VariableSistema.id == item['id'], VariableSistema.estatus == 1
            ).first()
            if not variable:
                errors.append({'index': idx, 'errors': ['Variable no encontrada']})
                continue
            if 'nombre' in item:
                variable.nombre = item['nombre']
            if 'valor' in item:
                variable.valor = item['valor']
            variable.updated_at = datetime.now()
            updated.append(variable)

        if updated:
            db.session.commit()
        response = {'updated': len(updated), 'data': VariableSistemaSchema.serialize_list(updated)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@variable_sistema_bp.route('/<string:oid>', methods=['DELETE'])
def delete_variable(oid):
    try:
        variable = VariableSistema.query.filter(
            VariableSistema.id == oid, VariableSistema.estatus == 1
        ).first()
        if not variable:
            return jsonify({'errors': ['Variable no encontrada']}), 404
        variable.estatus = -1
        variable.updated_at = datetime.now()
        db.session.commit()
        return jsonify({'message': 'Variable desactivada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@variable_sistema_bp.route('/list', methods=['POST'])
def get_variable_list():
    try:
        data = request.get_json()
        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400
        oid_list = data.get('oid_list', [])
        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400
        variables = VariableSistema.query.filter(
            VariableSistema.id.in_(oid_list), VariableSistema.estatus == 1
        ).all()
        return jsonify(VariableSistemaSchema.serialize_list(variables)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
