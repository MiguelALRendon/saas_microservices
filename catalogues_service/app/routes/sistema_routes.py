# Migrado a galurensoft_core.crud (build_blueprint). Doble unicidad: clave + api_key.
from app import db
from app.models.sistema import Sistema
from app.schemas.sistema_schema import SistemaSchema
from galurensoft_core.crud import ResourceDescriptor, build_blueprint

sistema_bp = build_blueprint(ResourceDescriptor(
    model=Sistema,
    name='sistema',
    url_prefix='/sistema',
    session=lambda: db.session,
    serialize=SistemaSchema.serialize,
    serialize_list=SistemaSchema.serialize_list,
    serialize_detail=SistemaSchema.serialize_detail,
    create_fields=['clave', 'nombre', 'descripcion', 'api_key'],
    editable=['clave', 'nombre', 'descripcion', 'api_key'],
    filters={'clave': 'ilike', 'nombre': 'ilike'},
    unique={'clave': 'La clave ya existe', 'api_key': 'El api_key ya existe'},
    conflict_status=400,
    validate_create=SistemaSchema.validate_create,
    validate_update=SistemaSchema.validate_update,
    not_found_message='Sistema no encontrado',
    delete_message='Sistema eliminado exitosamente',
    not_a_list_message='Se esperaba una lista de sistemas',
    include_has_more=False,
))
