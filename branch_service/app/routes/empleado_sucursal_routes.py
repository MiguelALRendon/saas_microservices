# Migrado a galurensoft_core.crud. Junction Empleado↔Sucursal: existencia de empleado +
# unicidad compuesta entre no-eliminados (permite re-asignar tras soft-delete). Validación -> 400.
from app import db
from app.enums import BaseObjectEstatus
from app.models.empleado import Empleado
from app.models.empleado_sucursal import EmpleadoSucursal
from app.schemas.empleado_sucursal_schema import EmpleadoSucursalSchema
from galurensoft_core.crud import ResourceDescriptor, build_blueprint
from galurensoft_core.persistence import StatusPolicy

_status = StatusPolicy.enum(enum_cls=BaseObjectEstatus)


def _validate_create(data):
    errors = EmpleadoSucursalSchema.validate_create(data)
    if not errors:
        empleado = Empleado.query.filter(
            Empleado.oid == data['fkEmpleado'],
            Empleado.estatus != BaseObjectEstatus.ELIMINADO,
        ).first()
        if not empleado:
            errors.append('El empleado no existe')
    return errors


empleado_sucursal_bp = build_blueprint(ResourceDescriptor(
    model=EmpleadoSucursal,
    name='empleado_sucursal',
    url_prefix='/empleado-sucursal',
    session=lambda: db.session,
    status=_status,
    serialize=EmpleadoSucursalSchema.serialize,
    serialize_list=EmpleadoSucursalSchema.serialize_list,
    create_fields=['fkEmpleado', 'fkSucursal'],
    editable=[],
    filters={'fkEmpleado': 'eq', 'fkSucursal': 'eq'},
    unique_together=[(('fkEmpleado', 'fkSucursal'), 'La asignación ya existe')],
    unique_visible_only=True,
    conflict_status=400,
    validation_status=400,
    validate_create=_validate_create,
    validate_update=EmpleadoSucursalSchema.validate_update,
    not_found_message='Asignación no encontrada',
    delete_message='Asignación eliminada exitosamente',
    not_a_list_message='Se esperaba una lista de asignaciones',
    include_has_more=False,
))
