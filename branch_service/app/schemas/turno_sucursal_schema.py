from .base_schema import BaseSchema
from app.enums import BaseObjectEstatus
from app.external_catalogues.empresa_external import EmpresaExternal
from app.external_catalogues.sucursal_external import SucursalExternal
from app.external_catalogues.sistema_external import SistemaExternal


class TurnoSucursalSchema(BaseSchema):
    """Schema para serialización y validación de TurnoSucursal."""

    @staticmethod
    def serialize(turno, _cache=None):
        """Plana — usa cache pasado si lo hay."""
        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        data = BaseSchema.serialize_base(turno)
        data.update({
            'nombre': turno.nombre,
            'hora_entrada': turno.hora_entrada.isoformat() if turno.hora_entrada else None,
            'hora_salida': turno.hora_salida.isoformat() if turno.hora_salida else None,
            'hora_corte': turno.hora_corte.isoformat() if turno.hora_corte else None,
            'fkEmpresa': turno.fkEmpresa,
            'empresa': BaseSchema.resolve_external(cache, 'empresa', turno.fkEmpresa, EmpresaExternal),
            'fkSucursal': turno.fkSucursal,
            'sucursal': BaseSchema.resolve_external(cache, 'sucursal', turno.fkSucursal, SucursalExternal),
            'fkSistema': turno.fkSistema,
            'sistema': BaseSchema.resolve_external(cache, 'sistema', turno.fkSistema, SistemaExternal),
        })
        return data

    @staticmethod
    def serialize_list(turnos, _cache=None):
        """Pre-batch de los 3 externals → 3 HTTPs totales sin importar N."""
        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        BaseSchema.prefetch_external(cache, 'empresa', [t.fkEmpresa for t in turnos], EmpresaExternal)
        BaseSchema.prefetch_external(cache, 'sucursal', [t.fkSucursal for t in turnos], SucursalExternal)
        BaseSchema.prefetch_external(cache, 'sistema', [t.fkSistema for t in turnos], SistemaExternal)
        return [TurnoSucursalSchema.serialize(t, _cache=cache) for t in turnos]

    @staticmethod
    def serialize_detail(turno, per_page: int = 25, _cache=None):
        """Detalle: turno_empleados paginado, omitiendo el lado 'turno' en cada junction."""
        from .turno_empleado_schema import TurnoEmpleadoSchema
        from app.models.turno_empleado import TurnoEmpleado

        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        data = TurnoSucursalSchema.serialize(turno, _cache=cache)

        junction_q = turno.turno_empleados.filter(TurnoEmpleado.estatus == BaseObjectEstatus.ACTIVO)
        data['turno_empleados'] = BaseSchema.paginate_local(
            junction_q,
            lambda items: [
                TurnoEmpleadoSchema.serialize_compact(te, omit='turno', _cache=cache)
                for te in items
            ],
            per_page=per_page,
        )
        return data

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('nombre'):
            errors.append('nombre es requerido')
        if not data.get('hora_entrada'):
            errors.append('hora_entrada es requerida')
        if not data.get('hora_salida'):
            errors.append('hora_salida es requerida')
        if not data.get('hora_corte'):
            errors.append('hora_corte es requerida')
        if not data.get('fkEmpresa'):
            errors.append('fkEmpresa es requerido')
        if not data.get('fkSucursal'):
            errors.append('fkSucursal es requerido')
        if not data.get('fkSistema'):
            errors.append('fkSistema es requerido')
        return errors

    @staticmethod
    def validate_update(data):
        return []
