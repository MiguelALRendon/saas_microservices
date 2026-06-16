# Migrado a galurensoft_core.crud (convención CONTINENTAL).
from app import db
from app.models.personaje_ficticio import PersonajeFicticio
from app.schemas.personaje_ficticio_schema import PersonajeFicticioSchema
from app.routes._helpers import slug_before_create
from galurensoft_core.crud import Hooks, ResourceDescriptor, build_blueprint
from galurensoft_core.persistence import CONTINENTAL, StatusPolicy

personaje_ficticio_bp = build_blueprint(ResourceDescriptor(
    model=PersonajeFicticio,
    name='personaje_ficticio',
    url_prefix='/personaje-ficticio',
    session=lambda: db.session,
    naming=CONTINENTAL,
    status=StatusPolicy.integer(),
    serialize=PersonajeFicticioSchema.serialize,
    serialize_list=PersonajeFicticioSchema.serialize_list,
    create_fields=['nombre', 'url_foto_perfil', 'descripcion', 'url_busqueda'],
    editable=['nombre', 'url_foto_perfil', 'descripcion', 'url_busqueda'],
    filters={'nombre': 'ilike'},
    validation_status=400,
    validate_create=PersonajeFicticioSchema.validate_create,
    validate_update=PersonajeFicticioSchema.validate_update,
    hooks=Hooks(before_create=slug_before_create(PersonajeFicticio, lambda d: d['nombre'])),
    not_found_message='Personaje no encontrado',
    delete_message='Personaje desactivado exitosamente',
    not_a_list_message='Se esperaba una lista de personajes',
    include_has_more=False,
))
