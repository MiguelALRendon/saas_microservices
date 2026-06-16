# Migrado a galurensoft_core.crud. Junction TurnoSucursal↔Empleado.
# La validación (existencia de turno/empleado, formato de fechas y unicidad compuesta sobre
# fkTurnoSucursal+fkEmpleado+diaSemana+fechaInicio entre no-eliminados) se concentra en
# validate_create (todo 400, mismo orden que el original). before_create/update coaccionan
# diaSemana (enum) y fechas. NOTA: existencia/unicidad ahora también en /many (consistencia).
from datetime import datetime

from app import db
from app.enums import BaseObjectEstatus, DiaSemana
from app.models.empleado import Empleado
from app.models.turno_empleado import TurnoEmpleado
from app.models.turno_sucursal import TurnoSucursal
from app.schemas.turno_empleado_schema import TurnoEmpleadoSchema
from galurensoft_core.crud import Hooks, ResourceDescriptor, build_blueprint
from galurensoft_core.persistence import StatusPolicy

_status = StatusPolicy.enum(enum_cls=BaseObjectEstatus)


def _parse_date(value):
    return datetime.strptime(value, '%Y-%m-%d').date()


def _validate_create(data):
    errors = TurnoEmpleadoSchema.validate_create(data)
    if errors:
        return errors

    turno = TurnoSucursal.query.filter(
        TurnoSucursal.oid == data['fkTurnoSucursal'],
        TurnoSucursal.estatus != BaseObjectEstatus.ELIMINADO,
    ).first()
    if not turno:
        return ['El turno especificado no existe']

    empleado = Empleado.query.filter(
        Empleado.oid == data['fkEmpleado'],
        Empleado.estatus != BaseObjectEstatus.ELIMINADO,
    ).first()
    if not empleado:
        return ['El empleado especificado no existe']

    try:
        fecha_inicio = _parse_date(data['fechaInicio'])
        if data.get('fechaFin'):
            _parse_date(data['fechaFin'])
    except ValueError:
        return ['fechaInicio/fechaFin con formato inválido (use YYYY-MM-DD)']

    existing = TurnoEmpleado.query.filter(
        TurnoEmpleado.fkTurnoSucursal == data['fkTurnoSucursal'],
        TurnoEmpleado.fkEmpleado == data['fkEmpleado'],
        TurnoEmpleado.diaSemana == DiaSemana[data['diaSemana']],
        TurnoEmpleado.fechaInicio == fecha_inicio,
        TurnoEmpleado.estatus != BaseObjectEstatus.ELIMINADO,
    ).first()
    if existing:
        return ['La asignación ya existe para esa fecha y día']
    return []


def _validate_update(data):
    errors = TurnoEmpleadoSchema.validate_update(data)
    for f in ('fechaInicio', 'fechaFin'):
        if data.get(f):
            try:
                _parse_date(data[f])
            except ValueError:
                errors.append(f'{f} con formato inválido (use YYYY-MM-DD)')
    return errors


def _coerce(data):
    out = dict(data)
    if isinstance(out.get('diaSemana'), str):
        out['diaSemana'] = DiaSemana[out['diaSemana']]
    if isinstance(out.get('fechaInicio'), str):
        out['fechaInicio'] = _parse_date(out['fechaInicio'])
    if isinstance(out.get('fechaFin'), str) and out['fechaFin']:
        out['fechaFin'] = _parse_date(out['fechaFin'])
    return out


turno_empleado_bp = build_blueprint(ResourceDescriptor(
    model=TurnoEmpleado,
    name='turno_empleado',
    url_prefix='/turno-empleado',
    session=lambda: db.session,
    status=_status,
    serialize=TurnoEmpleadoSchema.serialize,
    serialize_list=TurnoEmpleadoSchema.serialize_list,
    create_fields=['fkTurnoSucursal', 'fkEmpleado', 'diaSemana', 'fechaInicio', 'fechaFin'],
    editable=['diaSemana', 'fechaInicio', 'fechaFin'],
    filters={
        'fkTurnoSucursal': 'eq',
        'fkEmpleado': 'eq',
        'diaSemana': lambda m, v: m.diaSemana == DiaSemana[v] if v in DiaSemana.__members__ else m.diaSemana.is_(None),
    },
    validation_status=400,
    validate_create=_validate_create,
    validate_update=_validate_update,
    hooks=Hooks(before_create=_coerce, before_update=lambda obj, data: _coerce(data)),
    not_found_message='Asignación no encontrada',
    delete_message='Asignación eliminada exitosamente',
    not_a_list_message='Se esperaba una lista de asignaciones',
    include_has_more=False,
))
