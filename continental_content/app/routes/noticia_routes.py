from datetime import datetime
from flask import Blueprint, request, jsonify
from app import db
from app.models.noticia import Noticia
from app.schemas.noticia_schema import NoticiaSchema
from app.utils import generate_unique_url_busqueda

noticia_bp = Blueprint('noticia', __name__, url_prefix='/noticia')


@noticia_bp.route('/<string:oid>', methods=['GET'])
def get_noticia(oid):
    try:
        noticia = Noticia.query.filter(Noticia.id == oid, Noticia.estatus == 1).first()
        if not noticia:
            return jsonify({'errors': ['Noticia no encontrada']}), 404
        return jsonify(NoticiaSchema.serialize(noticia)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@noticia_bp.route('/', methods=['GET'])
def get_noticias():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        titulo = request.args.get('titulo', type=str)
        autor_id = request.args.get('autor_id', type=str)

        query = Noticia.query.filter(Noticia.estatus == 1).order_by(Noticia.created_at.desc())
        if titulo:
            query = query.filter(Noticia.titulo.ilike(f'%{titulo}%'))
        if autor_id:
            query = query.filter(Noticia.autor_id == autor_id)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'data': NoticiaSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@noticia_bp.route('/', methods=['POST'])
def create_noticia():
    try:
        data = request.get_json()
        errors = NoticiaSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 400

        url_busqueda = data.get('url_busqueda') or generate_unique_url_busqueda(data['titulo'], Noticia)
        noticia = Noticia(
            titulo=data['titulo'],
            descripcion_larga=data.get('descripcion_larga'),
            descripcion_corta=data.get('descripcion_corta'),
            url_portada=data.get('url_portada'),
            texto_noticia=data.get('texto_noticia'),
            autor_id=data.get('autor_id'),
            url_busqueda=url_busqueda,
            estatus=1,
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
        db.session.add(noticia)
        db.session.commit()
        return jsonify(NoticiaSchema.serialize(noticia)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@noticia_bp.route('/many', methods=['POST'])
def create_many_noticias():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de noticias']}), 400

        created, errors = [], []
        for idx, item in enumerate(data):
            validation_errors = NoticiaSchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            url_busqueda = item.get('url_busqueda') or generate_unique_url_busqueda(item['titulo'], Noticia)
            noticia = Noticia(
                titulo=item['titulo'],
                descripcion_larga=item.get('descripcion_larga'),
                descripcion_corta=item.get('descripcion_corta'),
                url_portada=item.get('url_portada'),
                texto_noticia=item.get('texto_noticia'),
                autor_id=item.get('autor_id'),
                url_busqueda=url_busqueda,
                estatus=1,
            )
            db.session.add(noticia)
            created.append(noticia)

        if created:
            db.session.commit()
        response = {'created': len(created), 'data': NoticiaSchema.serialize_list(created)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@noticia_bp.route('/<string:oid>', methods=['PUT'])
def update_noticia(oid):
    try:
        noticia = Noticia.query.filter(Noticia.id == oid, Noticia.estatus == 1).first()
        if not noticia:
            return jsonify({'errors': ['Noticia no encontrada']}), 404

        data = request.get_json()
        all_fields = [
            'titulo', 'descripcion_larga', 'descripcion_corta', 'url_portada',
            'texto_noticia', 'autor_id', 'url_busqueda', 'titulo_seo', 'descripcion_seo',
            'slug', 'keywords', 'canonical_url', 'no_index', 'no_follow', 'og_title',
            'og_description', 'og_image', 'og_type', 'og_url', 'alt_text_image',
            'schema_type', 'tags', 'social_sharing_enabled', 'seo_score',
        ]
        for field in all_fields:
            if field in data:
                setattr(noticia, field, data[field])

        noticia.updated_at = datetime.now()
        db.session.commit()
        return jsonify(NoticiaSchema.serialize(noticia)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@noticia_bp.route('/many', methods=['PUT'])
def update_many_noticias():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de noticias']}), 400

        updated, errors = [], []
        all_fields = [
            'titulo', 'descripcion_larga', 'descripcion_corta', 'url_portada',
            'texto_noticia', 'autor_id', 'url_busqueda',
        ]
        for idx, item in enumerate(data):
            if 'id' not in item:
                errors.append({'index': idx, 'errors': ['id es requerido']})
                continue
            noticia = Noticia.query.filter(Noticia.id == item['id'], Noticia.estatus == 1).first()
            if not noticia:
                errors.append({'index': idx, 'errors': ['Noticia no encontrada']})
                continue
            for field in all_fields:
                if field in item:
                    setattr(noticia, field, item[field])
            noticia.updated_at = datetime.now()
            updated.append(noticia)

        if updated:
            db.session.commit()
        response = {'updated': len(updated), 'data': NoticiaSchema.serialize_list(updated)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@noticia_bp.route('/<string:oid>', methods=['DELETE'])
def delete_noticia(oid):
    try:
        noticia = Noticia.query.filter(Noticia.id == oid, Noticia.estatus == 1).first()
        if not noticia:
            return jsonify({'errors': ['Noticia no encontrada']}), 404
        noticia.estatus = -1
        noticia.updated_at = datetime.now()
        db.session.commit()
        return jsonify({'message': 'Noticia desactivada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@noticia_bp.route('/list', methods=['POST'])
def get_noticia_list():
    try:
        data = request.get_json()
        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400
        oid_list = data.get('oid_list', [])
        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400
        noticias = Noticia.query.filter(
            Noticia.id.in_(oid_list), Noticia.estatus == 1
        ).all()
        return jsonify(NoticiaSchema.serialize_list(noticias)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
