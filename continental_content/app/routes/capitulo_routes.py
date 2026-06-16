# Migrado a galurensoft_core.crud (convención CONTINENTAL + SEO + FK obra).
from app import db
from app.models.capitulo import Capitulo
from app.models.obra import Obra
from app.schemas.capitulo_schema import CapituloSchema
from app.routes._helpers import SEO_FIELDS, slug_before_create
from galurensoft_core.crud import Hooks, ResourceDescriptor, build_blueprint
from galurensoft_core.persistence import CONTINENTAL, StatusPolicy

_CONTENT = ['titulo', 'descripcion_larga', 'descripcion_corta', 'url_portada', 'texto_capitulo',
            'comentario_creador', 'numero_capitulo', 'subarco_id', 'obra_id']
_FIELDS = _CONTENT + SEO_FIELDS + ['url_busqueda']


def _validate_create(data):
    errors = CapituloSchema.validate_create(data)
    if not errors:
        obra = Obra.query.filter(Obra.id == data['obra_id'], Obra.estatus == 1).first()
        if not obra:
            errors.append('La obra especificada no existe')
    return errors


def _slug_base(data):
    return data.get('titulo') or f"capitulo-{data.get('numero_capitulo', '')}"


capitulo_bp = build_blueprint(ResourceDescriptor(
    model=Capitulo,
    name='capitulo',
    url_prefix='/capitulo',
    session=lambda: db.session,
    naming=CONTINENTAL,
    status=StatusPolicy.integer(),
    serialize=CapituloSchema.serialize,
    serialize_list=CapituloSchema.serialize_list,
    create_fields=_FIELDS,
    editable=_FIELDS,
    filters={'titulo': 'ilike', 'obra_id': 'eq', 'subarco_id': 'eq'},
    validation_status=400,
    validate_create=_validate_create,
    validate_update=CapituloSchema.validate_update,
    hooks=Hooks(before_create=slug_before_create(Capitulo, _slug_base)),
    not_found_message='Capítulo no encontrado',
    delete_message='Capítulo desactivado exitosamente',
    not_a_list_message='Se esperaba una lista de capítulos',
    include_has_more=False,
))
