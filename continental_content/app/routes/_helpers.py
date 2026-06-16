"""Helpers compartidos para las rutas migradas a galurensoft_core.

- SEO_FIELDS: campos SEO comunes (SeoMixin) para create_fields/editable.
- slug_before_create: hook que genera url_busqueda único si no viene en el payload.
- hard_delete_extra: registra un DELETE de borrado físico para entidades ConceptBase
  (fecha, nota) que NO tienen estatus (no hay soft-delete).
"""
from flask import jsonify

from app import db
from app.utils import generate_unique_url_busqueda
from galurensoft_core.web import handle_errors

SEO_FIELDS = [
    'titulo_seo', 'descripcion_seo', 'slug', 'keywords', 'canonical_url',
    'no_index', 'no_follow', 'og_title', 'og_description', 'og_image',
    'og_type', 'og_url', 'alt_text_image', 'schema_type', 'tags',
    'social_sharing_enabled', 'seo_score',
]


def slug_before_create(model, base_fn):
    """Hook before_create: setea url_busqueda único (si no se proveyó)."""
    def hook(data):
        if data.get('url_busqueda'):
            return data
        return {**data, 'url_busqueda': generate_unique_url_busqueda(base_fn(data), model)}
    return hook


def hard_delete_extra(model, *, not_found, message):
    """Devuelve un `extra` que añade DELETE /<oid> con borrado físico (ConceptBase)."""
    def register(bp):
        @bp.route('/<string:oid>', methods=['DELETE'], endpoint='hard_delete')
        @handle_errors(rollback=lambda: db.session.rollback())
        def _delete(oid):
            obj = model.query.filter(model.id == oid).first()
            if obj is None:
                return jsonify({'errors': [not_found]}), 404
            db.session.delete(obj)
            db.session.commit()
            return jsonify({'message': message}), 200
    return register
