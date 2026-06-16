# Migrado a galurensoft_core.crud. Junction Usuario↔Empleado (Empleado en branch_service).
# Validación/conflicto -> 400; verifica existencia del usuario; unicidad compuesta entre
# registros NO eliminados (permite re-asignar tras soft-delete). NOTA: la verificación de
# existencia ahora también aplica en /many (consistencia; el original solo la hacía en el alta simple).
from app import db
from app.enums import BaseObjectEstatus
from app.models.usuario import Usuario
from app.models.usuario_empleado import UsuarioEmpleado
from app.schemas.usuario_empleado_schema import UsuarioEmpleadoSchema
from galurensoft_core.crud import ResourceDescriptor, build_blueprint


def _validate_create(data):
    errors = UsuarioEmpleadoSchema.validate_create(data)
    if not errors:
        usuario = Usuario.query.filter(
            Usuario.oid == data['fkUsuario'],
            Usuario.estatus != BaseObjectEstatus.ELIMINADO,
        ).first()
        if not usuario:
            errors.append('El usuario no existe')
    return errors


usuario_empleado_bp = build_blueprint(ResourceDescriptor(
    model=UsuarioEmpleado,
    name='usuario_empleado',
    url_prefix='/usuario-empleado',
    session=lambda: db.session,
    serialize=UsuarioEmpleadoSchema.serialize,
    serialize_list=UsuarioEmpleadoSchema.serialize_list,
    create_fields=['fkUsuario', 'fkEmpleado'],
    editable=[],
    filters={'fkUsuario': 'eq', 'fkEmpleado': 'eq'},
    unique_together=[(('fkUsuario', 'fkEmpleado'), 'La asignación ya existe')],
    unique_visible_only=True,
    conflict_status=400,
    validation_status=400,
    validate_create=_validate_create,
    validate_update=UsuarioEmpleadoSchema.validate_update,
    not_found_message='Asignación no encontrada',
    delete_message='Asignación eliminada exitosamente',
    not_a_list_message='Se esperaba una lista de asignaciones',
    include_has_more=False,
))
