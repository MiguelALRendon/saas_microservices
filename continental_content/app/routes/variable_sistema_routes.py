# Migrado a galurensoft_core.crud (convención CONTINENTAL).
from app import db
from app.models.variable_sistema import VariableSistema
from app.schemas.variable_sistema_schema import VariableSistemaSchema
from app.routes._helpers import slug_before_create
from galurensoft_core.crud import Hooks, ResourceDescriptor, build_blueprint
from galurensoft_core.persistence import CONTINENTAL, StatusPolicy

variable_sistema_bp = build_blueprint(ResourceDescriptor(
    model=VariableSistema,
    name='variable_sistema',
    url_prefix='/variable-sistema',
    session=lambda: db.session,
    naming=CONTINENTAL,
    status=StatusPolicy.integer(),
    serialize=VariableSistemaSchema.serialize,
    serialize_list=VariableSistemaSchema.serialize_list,
    create_fields=['nombre', 'valor', 'url_busqueda'],
    editable=['nombre', 'valor', 'url_busqueda'],
    filters={'nombre': 'ilike'},
    validation_status=400,
    validate_create=VariableSistemaSchema.validate_create,
    validate_update=VariableSistemaSchema.validate_update,
    hooks=Hooks(before_create=slug_before_create(VariableSistema, lambda d: d['nombre'])),
    not_found_message='Variable no encontrada',
    delete_message='Variable desactivada exitosamente',
    not_a_list_message='Se esperaba una lista de variables',
    include_has_more=False,
))
