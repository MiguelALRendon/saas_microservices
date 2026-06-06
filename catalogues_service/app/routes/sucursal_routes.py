# Migrado a galurensoft_core.crud: los 8 endpoints CRUD (GET/<oid>, GET/, POST/, POST/many,
# PUT/<oid>, PUT/many, DELETE/<oid>, POST/list) se generan declarativamente desde un
# ResourceDescriptor, reemplazando ~338 líneas de boilerplate. Los mensajes específicos de
# entidad y el envelope sin has_more se configuran para preservar el contrato JSON exacto.
from app import db
from app.models.sucursal import Sucursal
from app.schemas.sucursal_schema import SucursalSchema
from galurensoft_core.crud import ResourceDescriptor, build_blueprint

sucursal_bp = build_blueprint(ResourceDescriptor(
    model=Sucursal,
    name='sucursal',
    url_prefix='/sucursal',
    session=lambda: db.session,
    serialize=SucursalSchema.serialize,
    serialize_list=SucursalSchema.serialize_list,
    serialize_detail=SucursalSchema.serialize_detail,
    create_fields=['clave', 'nombre', 'folio', 'direccion', 'telefono', 'fkEmpresa'],
    editable=['clave', 'nombre', 'folio', 'direccion', 'telefono', 'fkEmpresa'],
    filters={'clave': 'ilike', 'nombre': 'ilike', 'fkEmpresa': 'eq'},
    unique={'clave': 'La clave ya existe'},
    validate_create=SucursalSchema.validate_create,
    validate_update=SucursalSchema.validate_update,
    not_found_message='Sucursal no encontrada',
    delete_message='Sucursal eliminada exitosamente',
    not_a_list_message='Se esperaba una lista de sucursales',
    include_has_more=False,
))
