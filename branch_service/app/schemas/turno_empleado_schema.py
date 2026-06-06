from .base_schema import BaseSchema
from .empleado_schema import EmpleadoSchema
from .turno_sucursal_schema import TurnoSucursalSchema
from app.enums import DiaSemana


class TurnoEmpleadoSchema(BaseSchema):
    """Junction TurnoSucursal ↔ Empleado (con atributos)."""

    @staticmethod
    def _serialize_attrs(te) -> dict:
        data = BaseSchema.serialize_base(te)
        data.update({
            'diaSemana': te.diaSemana.value if te.diaSemana else None,
            'fechaInicio': te.fechaInicio.isoformat() if te.fechaInicio else None,
            'fechaFin': te.fechaFin.isoformat() if te.fechaFin else None,
        })
        return data

    @staticmethod
    def serialize(te, _cache=None):
        """Completa — ambos lados resueltos."""
        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        data = TurnoEmpleadoSchema._serialize_attrs(te)
        data['fkTurnoSucursal'] = te.fkTurnoSucursal
        data['turno'] = TurnoSucursalSchema.serialize(te.turno, _cache=cache) if te.turno else None
        data['fkEmpleado'] = te.fkEmpleado
        data['empleado'] = EmpleadoSchema.serialize(te.empleado, _cache=cache) if te.empleado else None
        return data

    @staticmethod
    def serialize_compact(te, omit: str, _cache=None):
        """Compacta omitiendo un lado. omit ∈ {'turno', 'empleado'}."""
        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        data = TurnoEmpleadoSchema._serialize_attrs(te)
        if omit != 'turno':
            data['fkTurnoSucursal'] = te.fkTurnoSucursal
            data['turno'] = TurnoSucursalSchema.serialize(te.turno, _cache=cache) if te.turno else None
        if omit != 'empleado':
            data['fkEmpleado'] = te.fkEmpleado
            data['empleado'] = EmpleadoSchema.serialize(te.empleado, _cache=cache) if te.empleado else None
        return data

    @staticmethod
    def serialize_list(items, _cache=None):
        """Pre-batch de externals de ambos lados anidados (turno y empleado)."""
        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        from app.external_catalogues.empresa_external import EmpresaExternal
        from app.external_catalogues.sucursal_external import SucursalExternal
        from app.external_catalogues.sistema_external import SistemaExternal

        # TurnoSucursal y Empleado tienen externals: empresa, sucursal (turno), sistema
        empresas_oids = []
        sucursales_oids = []
        sistemas_oids = []
        for te in items:
            if te.turno:
                empresas_oids.append(te.turno.fkEmpresa)
                sucursales_oids.append(te.turno.fkSucursal)
                sistemas_oids.append(te.turno.fkSistema)
            if te.empleado:
                empresas_oids.append(te.empleado.fkEmpresa)
                sistemas_oids.append(te.empleado.fkSistema)

        BaseSchema.prefetch_external(cache, 'empresa', empresas_oids, EmpresaExternal)
        BaseSchema.prefetch_external(cache, 'sucursal', sucursales_oids, SucursalExternal)
        BaseSchema.prefetch_external(cache, 'sistema', sistemas_oids, SistemaExternal)
        return [TurnoEmpleadoSchema.serialize(te, _cache=cache) for te in items]

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('fkTurnoSucursal'):
            errors.append('fkTurnoSucursal es requerido')
        if not data.get('fkEmpleado'):
            errors.append('fkEmpleado es requerido')
        if not data.get('diaSemana'):
            errors.append('diaSemana es requerido')
        elif data['diaSemana'] not in DiaSemana.__members__:
            errors.append('diaSemana debe ser uno de: ' + ', '.join(DiaSemana.__members__.keys()))
        if not data.get('fechaInicio'):
            errors.append('fechaInicio es requerida')
        return errors

    @staticmethod
    def validate_update(data):
        errors = []
        if 'diaSemana' in data and data['diaSemana'] not in DiaSemana.__members__:
            errors.append('diaSemana debe ser uno de: ' + ', '.join(DiaSemana.__members__.keys()))
        return errors
