# Migrado a galurensoft_core.crud. fecha_contratacion se parsea (YYYY-MM-DD) con hooks;
# existencia de cargo en validate_create; CURP único (si se provee). Validación -> 400.
from datetime import datetime

from app import db
from app.enums import BaseObjectEstatus
from app.models.cargo import Cargo
from app.models.empleado import Empleado
from app.models.empleado_sucursal import EmpleadoSucursal
from app.schemas.empleado_schema import EmpleadoSchema
from galurensoft_core.crud import Hooks, ResourceDescriptor, build_blueprint
from galurensoft_core.persistence import StatusPolicy

_status = StatusPolicy.enum(enum_cls=BaseObjectEstatus)


def _validate_create(data):
    errors = EmpleadoSchema.validate_create(data)
    if not errors:
        cargo = Cargo.query.filter(
            Cargo.oid == data['fkCargo'],
            Cargo.estatus != BaseObjectEstatus.ELIMINADO,
        ).first()
        if not cargo:
            errors.append('El cargo especificado no existe')
    return errors


def _parse_fecha(data):
    if isinstance(data.get('fecha_contratacion'), str):
        return {**data, 'fecha_contratacion': datetime.strptime(data['fecha_contratacion'], '%Y-%m-%d').date()}
    return data


def _filter_by_sucursal(model, value):
    return model.empleado_sucursales.any(
        (EmpleadoSucursal.fkSucursal == value)
        & (EmpleadoSucursal.estatus != BaseObjectEstatus.ELIMINADO)
    )


empleado_bp = build_blueprint(ResourceDescriptor(
    model=Empleado,
    name='empleado',
    url_prefix='/empleado',
    session=lambda: db.session,
    status=_status,
    serialize=EmpleadoSchema.serialize,
    serialize_list=EmpleadoSchema.serialize_list,
    serialize_detail=EmpleadoSchema.serialize_detail,
    create_fields=['nombres', 'apellido_paterno', 'apellido_materno', 'curp', 'rfc',
                   'fecha_contratacion', 'telefono', 'email', 'fkCargo', 'fkEmpresa', 'fkSistema'],
    editable=['nombres', 'apellido_paterno', 'apellido_materno', 'curp', 'rfc',
              'fecha_contratacion', 'telefono', 'email', 'fkCargo', 'fkEmpresa', 'fkSistema'],
    filters={'fkCargo': 'eq', 'fkSucursal': _filter_by_sucursal},
    unique={'curp': 'El CURP ya está registrado'},
    conflict_status=400,
    validation_status=400,
    validate_create=_validate_create,
    validate_update=EmpleadoSchema.validate_update,
    hooks=Hooks(before_create=_parse_fecha, before_update=lambda obj, data: _parse_fecha(data)),
    not_found_message='Empleado no encontrado',
    delete_message='Empleado eliminado exitosamente',
    not_a_list_message='Se esperaba una lista de empleados',
    include_has_more=False,
))
