# Migrado a galurensoft_core.crud. fecha (DateTime) se parsea con fromisoformat; existencia
# de turno en validate_create; filtro de rango fecha_inicio/fecha_fin. Validación -> 400.
from datetime import datetime

from app import db
from app.enums import BaseObjectEstatus
from app.models.corte_caja import CorteCaja
from app.models.turno_sucursal import TurnoSucursal
from app.schemas.corte_caja_schema import CorteCajaSchema
from galurensoft_core.crud import Hooks, ResourceDescriptor, build_blueprint
from galurensoft_core.persistence import StatusPolicy

_status = StatusPolicy.enum(enum_cls=BaseObjectEstatus)


def _validate_create(data):
    errors = CorteCajaSchema.validate_create(data)
    if not errors:
        turno = TurnoSucursal.query.filter(
            TurnoSucursal.oid == data['fkTurno'],
            TurnoSucursal.estatus != BaseObjectEstatus.ELIMINADO,
        ).first()
        if not turno:
            errors.append('El turno especificado no existe')
    return errors


def _parse_fecha(data):
    if isinstance(data.get('fecha'), str):
        return {**data, 'fecha': datetime.fromisoformat(data['fecha'])}
    return data


corte_caja_bp = build_blueprint(ResourceDescriptor(
    model=CorteCaja,
    name='corte_caja',
    url_prefix='/corte_caja',
    session=lambda: db.session,
    status=_status,
    serialize=CorteCajaSchema.serialize,
    serialize_list=CorteCajaSchema.serialize_list,
    create_fields=['fecha', 'monto_inicial', 'monto_final', 'esperado', 'diferencia',
                   'fkEmpresa', 'fkSucursal', 'fkUsuario', 'fkTurno', 'fkSistema'],
    editable=['fecha', 'monto_inicial', 'monto_final', 'esperado', 'diferencia',
              'fkEmpresa', 'fkSucursal', 'fkUsuario', 'fkTurno', 'fkSistema'],
    filters={
        'fkEmpresa': 'eq', 'fkSucursal': 'eq', 'fkUsuario': 'eq', 'fkTurno': 'eq',
        'fecha_inicio': lambda m, v: m.fecha >= datetime.strptime(v, '%Y-%m-%d'),
        'fecha_fin': lambda m, v: m.fecha <= datetime.strptime(v, '%Y-%m-%d'),
    },
    validation_status=400,
    validate_create=_validate_create,
    validate_update=CorteCajaSchema.validate_update,
    hooks=Hooks(before_create=_parse_fecha, before_update=lambda obj, data: _parse_fecha(data)),
    not_found_message='Corte de caja no encontrado',
    delete_message='Corte de caja eliminado exitosamente',
    not_a_list_message='Se esperaba una lista de cortes de caja',
    include_has_more=False,
))
