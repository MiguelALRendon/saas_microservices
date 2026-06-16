# Migrado a galurensoft_core.crud. Fecha es ConceptBase (sin estatus): borrado FÍSICO.
from datetime import datetime

from app import db
from app.models.fecha import Fecha
from app.schemas.fecha_schema import FechaSchema
from app.routes._helpers import hard_delete_extra
from galurensoft_core.crud import Hooks, ResourceDescriptor, build_blueprint
from galurensoft_core.persistence import CONTINENTAL

_ENDPOINTS = ('get_one', 'get_list', 'create', 'create_many', 'update', 'update_many', 'list')


def _validate_create(data):
    errors = FechaSchema.validate_create(data)
    if not errors:
        try:
            datetime.strptime(data['fecha'], '%Y-%m-%d')
        except ValueError:
            errors.append('fecha debe tener formato YYYY-MM-DD')
    return errors


def _parse_fecha(data):
    if isinstance(data.get('fecha'), str):
        return {**data, 'fecha': datetime.strptime(data['fecha'], '%Y-%m-%d').date()}
    return data


fecha_bp = build_blueprint(
    ResourceDescriptor(
        model=Fecha,
        name='fecha',
        url_prefix='/fecha',
        session=lambda: db.session,
        naming=CONTINENTAL,
        status=None,  # ConceptBase: sin estatus
        serialize=FechaSchema.serialize,
        serialize_list=FechaSchema.serialize_list,
        create_fields=['fecha', 'evento'],
        editable=['fecha', 'evento'],
        validation_status=400,
        validate_create=_validate_create,
        validate_update=FechaSchema.validate_update,
        hooks=Hooks(before_create=_parse_fecha, before_update=lambda obj, data: _parse_fecha(data)),
        not_found_message='Fecha no encontrada',
        not_a_list_message='Se esperaba una lista de fechas',
        include_has_more=False,
    ),
    endpoints=_ENDPOINTS,
    extra=hard_delete_extra(Fecha, not_found='Fecha no encontrada', message='Fecha eliminada exitosamente'),
)
