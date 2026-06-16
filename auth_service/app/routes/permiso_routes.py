# Migrado a galurensoft_core.crud.
# FIX: el original validaba fkSistema pero no lo persistía (NOT NULL) -> create 500;
# aquí fkSistema se incluye en create_fields.
from app import db
from app.models.permiso_nuevo import Permiso
from app.schemas.permiso_schema import PermisoSchema
from galurensoft_core.crud import ResourceDescriptor, build_blueprint

permiso_bp = build_blueprint(ResourceDescriptor(
    model=Permiso,
    name='permiso',
    url_prefix='/permiso',
    session=lambda: db.session,
    serialize=PermisoSchema.serialize,
    serialize_list=PermisoSchema.serialize_list,
    create_fields=['clave', 'nombre', 'permiso', 'fkSistema'],
    editable=['clave', 'nombre', 'permiso'],
    filters={'clave': 'ilike', 'nombre': 'ilike', 'permiso': 'ilike'},
    unique={'clave': 'La clave ya existe'},
    conflict_status=400,
    validation_status=422,
    validate_create=PermisoSchema.validate_create,
    validate_update=PermisoSchema.validate_update,
    not_found_message='Permiso no encontrado',
    delete_message='Permiso eliminado exitosamente',
    not_a_list_message='Se esperaba una lista de permisos',
    include_has_more=False,
))
