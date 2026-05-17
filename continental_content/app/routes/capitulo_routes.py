from datetime import datetime
from flask import Blueprint, request, jsonify
from app import db
from app.models.capitulo import Capitulo
from app.models.obra import Obra
from app.schemas.capitulo_schema import CapituloSchema
from app.utils import generate_unique_url_busqueda

capitulo_bp = Blueprint('capitulo', __name__, url_prefix='/capitulo')


@capitulo_bp.route('/<string:oid>', methods=['GET'])
def get_capitulo(oid):
    try:
        capitulo = Capitulo.query.filter(Capitulo.id == oid, Capitulo.estatus == 1).first()
        if not capitulo:
            return jsonify({'errors': ['Capítulo no encontrado']}), 404
        return jsonify(CapituloSchema.serialize(capitulo)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@capitulo_bp.route('/', methods=['GET'])
def get_capitulos():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        titulo = request.args.get('titulo', type=str)
        obra_id = request.args.get('obra_id', type=str)
        subarco_id = request.args.get('subarco_id', type=str)

        query = Capitulo.query.filter(Capitulo.estatus == 1).order_by(Capitulo.numero_capitulo.asc())
        if titulo:
            query = query.filter(Capitulo.titulo.ilike(f'%{titulo}%'))
        if obra_id:
            query = query.filter(Capitulo.obra_id == obra_id)
        if subarco_id:
            query = query.filter(Capitulo.subarco_id == subarco_id)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'data': CapituloSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@capitulo_bp.route('/', methods=['POST'])
def create_capitulo():
    try:
        data = request.get_json()
        errors = CapituloSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 400

        # Validar que la obra existe
        obra = Obra.query.filter(Obra.id == data['obra_id'], Obra.estatus == 1).first()
        if not obra:
            return jsonify({'errors': ['La obra especificada no existe']}), 400

        titulo_base = data.get('titulo', f"capitulo-{data.get('numero_capitulo', '')}")
        url_busqueda = data.get('url_busqueda') or generate_unique_url_busqueda(titulo_base, Capitulo)

        capitulo = Capitulo(
            titulo=data['titulo'],
            descripcion_larga=data.get('descripcion_larga'),
            descripcion_corta=data.get('descripcion_corta'),
            url_portada=data.get('url_portada'),
            texto_capitulo=data.get('texto_capitulo'),
            comentario_creador=data.get('comentario_creador'),
            numero_capitulo=data['numero_capitulo'],
            subarco_id=data.get('subarco_id'),
            obra_id=data['obra_id'],
            url_busqueda=url_busqueda,
            estatus=1,
            # SEO fields
            titulo_seo=data.get('titulo_seo'),
            descripcion_seo=data.get('descripcion_seo'),
            slug=data.get('slug'),
            keywords=data.get('keywords'),
            canonical_url=data.get('canonical_url'),
            no_index=data.get('no_index', False),
            no_follow=data.get('no_follow', False),
            og_title=data.get('og_title'),
            og_description=data.get('og_description'),
            og_image=data.get('og_image'),
            og_type=data.get('og_type'),
            og_url=data.get('og_url'),
            alt_text_image=data.get('alt_text_image'),
            schema_type=data.get('schema_type'),
            tags=data.get('tags'),
            social_sharing_enabled=data.get('social_sharing_enabled', True),
            seo_score=data.get('seo_score'),
        )
        db.session.add(capitulo)
        db.session.commit()
        return jsonify(CapituloSchema.serialize(capitulo)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@capitulo_bp.route('/many', methods=['POST'])
def create_many_capitulos():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de capítulos']}), 400

        created, errors = [], []
        for idx, item in enumerate(data):
            validation_errors = CapituloSchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            titulo_base = item.get('titulo', f"capitulo-{item.get('numero_capitulo', '')}")
            url_busqueda = item.get('url_busqueda') or generate_unique_url_busqueda(titulo_base, Capitulo)
            capitulo = Capitulo(
                titulo=item['titulo'],
                descripcion_larga=item.get('descripcion_larga'),
                descripcion_corta=item.get('descripcion_corta'),
                url_portada=item.get('url_portada'),
                texto_capitulo=item.get('texto_capitulo'),
                comentario_creador=item.get('comentario_creador'),
                numero_capitulo=item['numero_capitulo'],
                subarco_id=item.get('subarco_id'),
                obra_id=item['obra_id'],
                url_busqueda=url_busqueda,
                estatus=1,
            )
            db.session.add(capitulo)
            created.append(capitulo)

        if created:
            db.session.commit()
        response = {'created': len(created), 'data': CapituloSchema.serialize_list(created)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@capitulo_bp.route('/<string:oid>', methods=['PUT'])
def update_capitulo(oid):
    try:
        capitulo = Capitulo.query.filter(Capitulo.id == oid, Capitulo.estatus == 1).first()
        if not capitulo:
            return jsonify({'errors': ['Capítulo no encontrado']}), 404

        data = request.get_json()
        seo_fields = [
            'titulo_seo', 'descripcion_seo', 'slug', 'keywords', 'canonical_url',
            'no_index', 'no_follow', 'og_title', 'og_description', 'og_image',
            'og_type', 'og_url', 'alt_text_image', 'schema_type', 'tags',
            'social_sharing_enabled', 'seo_score',
        ]
        content_fields = [
            'titulo', 'descripcion_larga', 'descripcion_corta', 'url_portada',
            'texto_capitulo', 'comentario_creador', 'numero_capitulo',
            'subarco_id', 'obra_id', 'url_busqueda',
        ]
        for field in content_fields + seo_fields:
            if field in data:
                setattr(capitulo, field, data[field])

        capitulo.updated_at = datetime.now()
        db.session.commit()
        return jsonify(CapituloSchema.serialize(capitulo)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@capitulo_bp.route('/many', methods=['PUT'])
def update_many_capitulos():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de capítulos']}), 400

        updated, errors = [], []
        all_fields = [
            'titulo', 'descripcion_larga', 'descripcion_corta', 'url_portada',
            'texto_capitulo', 'comentario_creador', 'numero_capitulo',
            'subarco_id', 'obra_id', 'url_busqueda', 'titulo_seo', 'descripcion_seo',
            'slug', 'keywords', 'canonical_url', 'no_index', 'no_follow',
            'og_title', 'og_description', 'og_image', 'og_type', 'og_url',
            'alt_text_image', 'schema_type', 'tags', 'social_sharing_enabled', 'seo_score',
        ]
        for idx, item in enumerate(data):
            if 'id' not in item:
                errors.append({'index': idx, 'errors': ['id es requerido']})
                continue
            capitulo = Capitulo.query.filter(Capitulo.id == item['id'], Capitulo.estatus == 1).first()
            if not capitulo:
                errors.append({'index': idx, 'errors': ['Capítulo no encontrado']})
                continue
            for field in all_fields:
                if field in item:
                    setattr(capitulo, field, item[field])
            capitulo.updated_at = datetime.now()
            updated.append(capitulo)

        if updated:
            db.session.commit()
        response = {'updated': len(updated), 'data': CapituloSchema.serialize_list(updated)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@capitulo_bp.route('/<string:oid>', methods=['DELETE'])
def delete_capitulo(oid):
    try:
        capitulo = Capitulo.query.filter(Capitulo.id == oid, Capitulo.estatus == 1).first()
        if not capitulo:
            return jsonify({'errors': ['Capítulo no encontrado']}), 404
        capitulo.estatus = -1
        capitulo.updated_at = datetime.now()
        db.session.commit()
        return jsonify({'message': 'Capítulo desactivado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@capitulo_bp.route('/list', methods=['POST'])
def get_capitulo_list():
    try:
        data = request.get_json()
        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400
        oid_list = data.get('oid_list', [])
        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400
        capitulos = Capitulo.query.filter(
            Capitulo.id.in_(oid_list), Capitulo.estatus == 1
        ).all()
        return jsonify(CapituloSchema.serialize_list(capitulos)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
