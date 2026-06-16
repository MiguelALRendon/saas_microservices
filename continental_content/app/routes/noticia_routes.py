# Migrado a galurensoft_core.crud (convención CONTINENTAL + SEO).
from app import db
from app.models.noticia import Noticia
from app.schemas.noticia_schema import NoticiaSchema
from app.routes._helpers import SEO_FIELDS, slug_before_create
from galurensoft_core.crud import Hooks, ResourceDescriptor, build_blueprint
from galurensoft_core.persistence import CONTINENTAL, StatusPolicy

_CONTENT = ['titulo', 'descripcion_larga', 'descripcion_corta', 'url_portada', 'texto_noticia', 'autor_id']
_FIELDS = _CONTENT + SEO_FIELDS + ['url_busqueda']

noticia_bp = build_blueprint(ResourceDescriptor(
    model=Noticia,
    name='noticia',
    url_prefix='/noticia',
    session=lambda: db.session,
    naming=CONTINENTAL,
    status=StatusPolicy.integer(),
    serialize=NoticiaSchema.serialize,
    serialize_list=NoticiaSchema.serialize_list,
    create_fields=_FIELDS,
    editable=_FIELDS,
    filters={'titulo': 'ilike', 'autor_id': 'eq'},
    validation_status=400,
    validate_create=NoticiaSchema.validate_create,
    validate_update=NoticiaSchema.validate_update,
    hooks=Hooks(before_create=slug_before_create(Noticia, lambda d: d['titulo'])),
    not_found_message='Noticia no encontrada',
    delete_message='Noticia desactivada exitosamente',
    not_a_list_message='Se esperaba una lista de noticias',
    include_has_more=False,
))
