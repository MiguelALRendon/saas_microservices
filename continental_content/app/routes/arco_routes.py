# Migrado a galurensoft_core.crud (convención CONTINENTAL).
from app import db
from app.models.arco import Arco
from app.schemas.arco_schema import ArcoSchema
from app.routes._helpers import slug_before_create
from galurensoft_core.crud import Hooks, ResourceDescriptor, build_blueprint
from galurensoft_core.persistence import CONTINENTAL, StatusPolicy

arco_bp = build_blueprint(ResourceDescriptor(
    model=Arco,
    name='arco',
    url_prefix='/arco',
    session=lambda: db.session,
    naming=CONTINENTAL,
    status=StatusPolicy.integer(),
    serialize=ArcoSchema.serialize,
    serialize_list=ArcoSchema.serialize_list,
    create_fields=['nombre', 'es_subarco', 'orden', 'url_busqueda'],
    editable=['nombre', 'es_subarco', 'orden', 'url_busqueda'],
    filters={'nombre': 'ilike', 'es_subarco': 'bool'},
    validation_status=400,
    validate_create=ArcoSchema.validate_create,
    validate_update=ArcoSchema.validate_update,
    hooks=Hooks(before_create=slug_before_create(Arco, lambda d: d['nombre'])),
    not_found_message='Arco no encontrado',
    delete_message='Arco desactivado exitosamente',
    not_a_list_message='Se esperaba una lista de arcos',
    include_has_more=False,
))
