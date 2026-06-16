# Migrado a galurensoft_core.crud. Junction Usuario↔Sucursal (Sucursal en catalogues_service).
# Igual que usuario_empleado: 400, existencia de usuario, unicidad entre no-eliminados.
from app import db
from app.enums import BaseObjectEstatus
from app.models.usuario import Usuario
from app.models.usuario_sucursal import UsuarioSucursal
from app.schemas.usuario_sucursal_schema import UsuarioSucursalSchema
from galurensoft_core.crud import ResourceDescriptor, build_blueprint


def _validate_create(data):
    errors = UsuarioSucursalSchema.validate_create(data)
    if not errors:
        usuario = Usuario.query.filter(
            Usuario.oid == data['fkUsuario'],
            Usuario.estatus != BaseObjectEstatus.ELIMINADO,
        ).first()
        if not usuario:
            errors.append('El usuario no existe')
    return errors


usuario_sucursal_bp = build_blueprint(ResourceDescriptor(
    model=UsuarioSucursal,
    name='usuario_sucursal',
    url_prefix='/usuario-sucursal',
    session=lambda: db.session,
    serialize=UsuarioSucursalSchema.serialize,
    serialize_list=UsuarioSucursalSchema.serialize_list,
    create_fields=['fkUsuario', 'fkSucursal'],
    editable=[],
    filters={'fkUsuario': 'eq', 'fkSucursal': 'eq'},
    unique_together=[(('fkUsuario', 'fkSucursal'), 'La asignación ya existe')],
    unique_visible_only=True,
    conflict_status=400,
    validation_status=400,
    validate_create=_validate_create,
    validate_update=UsuarioSucursalSchema.validate_update,
    not_found_message='Asignación no encontrada',
    delete_message='Asignación eliminada exitosamente',
    not_a_list_message='Se esperaba una lista de asignaciones',
    include_has_more=False,
))
