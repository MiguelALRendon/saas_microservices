# Migrado a galurensoft_core.crud (convención CONTINENTAL: id/Integer/url_busqueda, soft-delete -1).
from app import db
from app.models.obra import Obra
from app.schemas.obra_schema import ObraSchema
from app.routes._helpers import slug_before_create
from galurensoft_core.crud import Hooks, ResourceDescriptor, build_blueprint
from galurensoft_core.persistence import CONTINENTAL, StatusPolicy

obra_bp = build_blueprint(ResourceDescriptor(
    model=Obra,
    name='obra',
    url_prefix='/obra',
    session=lambda: db.session,
    naming=CONTINENTAL,
    status=StatusPolicy.integer(),
    serialize=ObraSchema.serialize,
    serialize_list=ObraSchema.serialize_list,
    create_fields=['nombre', 'descripcion', 'url_portada', 'orden', 'icono', 'url_busqueda'],
    editable=['nombre', 'descripcion', 'url_portada', 'orden', 'icono', 'url_busqueda'],
    filters={'nombre': 'ilike'},
    validation_status=400,
    validate_create=ObraSchema.validate_create,
    validate_update=ObraSchema.validate_update,
    hooks=Hooks(before_create=slug_before_create(Obra, lambda d: d['nombre'])),
    not_found_message='Obra no encontrada',
    delete_message='Obra desactivada exitosamente',
    not_a_list_message='Se esperaba una lista de obras',
    include_has_more=False,
))
