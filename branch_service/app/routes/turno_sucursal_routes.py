# Migrado a galurensoft_core.crud. hora_entrada/salida/corte se parsean (HH:MM:SS) con hooks.
from datetime import datetime

from app import db
from app.enums import BaseObjectEstatus
from app.models.turno_sucursal import TurnoSucursal
from app.schemas.turno_sucursal_schema import TurnoSucursalSchema
from galurensoft_core.crud import Hooks, ResourceDescriptor, build_blueprint
from galurensoft_core.persistence import StatusPolicy

_status = StatusPolicy.enum(enum_cls=BaseObjectEstatus)
_HORAS = ('hora_entrada', 'hora_salida', 'hora_corte')


def _parse_horas(data):
    out = dict(data)
    for f in _HORAS:
        if isinstance(out.get(f), str):
            out[f] = datetime.strptime(out[f], '%H:%M:%S').time()
    return out


turno_sucursal_bp = build_blueprint(ResourceDescriptor(
    model=TurnoSucursal,
    name='turno_sucursal',
    url_prefix='/turno-sucursal',
    session=lambda: db.session,
    status=_status,
    serialize=TurnoSucursalSchema.serialize,
    serialize_list=TurnoSucursalSchema.serialize_list,
    serialize_detail=TurnoSucursalSchema.serialize_detail,
    create_fields=['nombre', 'hora_entrada', 'hora_salida', 'hora_corte', 'fkEmpresa', 'fkSucursal', 'fkSistema'],
    editable=['nombre', 'hora_entrada', 'hora_salida', 'hora_corte', 'fkEmpresa', 'fkSucursal', 'fkSistema'],
    filters={'nombre': 'ilike', 'fkEmpresa': 'eq', 'fkSucursal': 'eq'},
    validation_status=400,
    validate_create=TurnoSucursalSchema.validate_create,
    validate_update=TurnoSucursalSchema.validate_update,
    hooks=Hooks(before_create=_parse_horas, before_update=lambda obj, data: _parse_horas(data)),
    not_found_message='Turno de sucursal no encontrado',
    delete_message='Turno de sucursal eliminado exitosamente',
    not_a_list_message='Se esperaba una lista de turnos',
    include_has_more=False,
))
