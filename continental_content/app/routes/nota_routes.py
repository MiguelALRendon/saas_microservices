from datetime import datetime, date
from flask import Blueprint, request, jsonify
from app import db
from app.models.nota import Nota
from app.models.obra import Obra
from app.schemas.nota_schema import NotaSchema

nota_bp = Blueprint('nota', __name__, url_prefix='/nota')


@nota_bp.route('/<string:oid>', methods=['GET'])
def get_nota(oid):
    try:
        nota = Nota.query.filter(Nota.id == oid).first()
        if not nota:
            return jsonify({'errors': ['Nota no encontrada']}), 404
        return jsonify(NotaSchema.serialize(nota)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@nota_bp.route('/', methods=['GET'])
def get_notas():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        fk_obra = request.args.get('fk_obra', type=str)
        fk_arco = request.args.get('fk_arco', type=str)

        query = Nota.query
        if fk_obra:
            query = query.filter(Nota.fk_obra == fk_obra)
        if fk_arco:
            query = query.filter(Nota.fk_arco == fk_arco)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'data': NotaSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@nota_bp.route('/', methods=['POST'])
def create_nota():
    try:
        data = request.get_json()
        errors = NotaSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 400

        # Validar que la obra existe
        obra = Obra.query.filter(Obra.id == data['fk_obra'], Obra.estatus == 1).first()
        if not obra:
            return jsonify({'errors': ['La obra especificada no existe']}), 400

        nota = Nota(
            titulo_nota=data['titulo_nota'],
            texto_nota=data['texto_nota'],
            fk_obra=data['fk_obra'],
            fk_arco=data.get('fk_arco'),
        )
        db.session.add(nota)
        db.session.commit()
        return jsonify(NotaSchema.serialize(nota)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@nota_bp.route('/many', methods=['POST'])
def create_many_notas():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de notas']}), 400

        created, errors = [], []
        for idx, item in enumerate(data):
            validation_errors = NotaSchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            nota = Nota(
                titulo_nota=item['titulo_nota'],
                texto_nota=item['texto_nota'],
                fk_obra=item['fk_obra'],
                fk_arco=item.get('fk_arco'),
            )
            db.session.add(nota)
            created.append(nota)

        if created:
            db.session.commit()
        response = {'created': len(created), 'data': NotaSchema.serialize_list(created)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@nota_bp.route('/<string:oid>', methods=['PUT'])
def update_nota(oid):
    try:
        nota = Nota.query.filter(Nota.id == oid).first()
        if not nota:
            return jsonify({'errors': ['Nota no encontrada']}), 404

        data = request.get_json()
        for field in ['titulo_nota', 'texto_nota', 'fk_obra', 'fk_arco']:
            if field in data:
                setattr(nota, field, data[field])

        nota.updated_at = datetime.now()
        db.session.commit()
        return jsonify(NotaSchema.serialize(nota)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@nota_bp.route('/many', methods=['PUT'])
def update_many_notas():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de notas']}), 400

        updated, errors = [], []
        for idx, item in enumerate(data):
            if 'id' not in item:
                errors.append({'index': idx, 'errors': ['id es requerido']})
                continue
            nota = Nota.query.filter(Nota.id == item['id']).first()
            if not nota:
                errors.append({'index': idx, 'errors': ['Nota no encontrada']})
                continue
            for field in ['titulo_nota', 'texto_nota', 'fk_obra', 'fk_arco']:
                if field in item:
                    setattr(nota, field, item[field])
            nota.updated_at = datetime.now()
            updated.append(nota)

        if updated:
            db.session.commit()
        response = {'updated': len(updated), 'data': NotaSchema.serialize_list(updated)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@nota_bp.route('/<string:oid>', methods=['DELETE'])
def delete_nota(oid):
    """Hard delete — Nota usa ConceptBase (sin estatus)."""
    try:
        nota = Nota.query.filter(Nota.id == oid).first()
        if not nota:
            return jsonify({'errors': ['Nota no encontrada']}), 404
        db.session.delete(nota)
        db.session.commit()
        return jsonify({'message': 'Nota eliminada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@nota_bp.route('/list', methods=['POST'])
def get_nota_list():
    try:
        data = request.get_json()
        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400
        oid_list = data.get('oid_list', [])
        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400
        notas = Nota.query.filter(Nota.id.in_(oid_list)).all()
        return jsonify(NotaSchema.serialize_list(notas)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
