from .base_schema import BaseSchema
from .empleado_schema import EmpleadoSchema
from app.external_catalogues.sucursal_external import SucursalExternal


class EmpleadoSucursalSchema(BaseSchema):
    """Junction Empleado ↔ Sucursal."""

    @staticmethod
    def serialize(es, _cache=None):
        """Completa — ambos lados resueltos."""
        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        data = BaseSchema.serialize_base(es)
        data.update({
            'fkEmpleado': es.fkEmpleado,
            'empleado': EmpleadoSchema.serialize(es.empleado, _cache=cache) if es.empleado else None,
            'fkSucursal': es.fkSucursal,
            'sucursal': BaseSchema.resolve_external(cache, 'sucursal', es.fkSucursal, SucursalExternal),
        })
        return data

    @staticmethod
    def serialize_compact(es, omit: str, _cache=None):
        """Compacta omitiendo un lado. omit ∈ {'empleado', 'sucursal'}."""
        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        data = BaseSchema.serialize_base(es)
        if omit != 'empleado':
            data['fkEmpleado'] = es.fkEmpleado
            data['empleado'] = EmpleadoSchema.serialize(es.empleado, _cache=cache) if es.empleado else None
        if omit != 'sucursal':
            data['fkSucursal'] = es.fkSucursal
            data['sucursal'] = BaseSchema.resolve_external(cache, 'sucursal', es.fkSucursal, SucursalExternal)
        return data

    @staticmethod
    def serialize_list(items, _cache=None):
        """Pre-batch: empleados (internos) no necesitan; sucursales (externas) sí."""
        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        # Empleado tiene externals (empresa, sistema): pre-batch para los empleados anidados
        empleados = [es.empleado for es in items if es.empleado]
        if empleados:
            from app.external_catalogues.empresa_external import EmpresaExternal
            from app.external_catalogues.sistema_external import SistemaExternal
            BaseSchema.prefetch_external(cache, 'empresa', [e.fkEmpresa for e in empleados], EmpresaExternal)
            BaseSchema.prefetch_external(cache, 'sistema', [e.fkSistema for e in empleados], SistemaExternal)
        # Sucursales en batch
        BaseSchema.prefetch_external(cache, 'sucursal', [es.fkSucursal for es in items], SucursalExternal)
        return [EmpleadoSucursalSchema.serialize(es, _cache=cache) for es in items]

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('fkEmpleado'):
            errors.append('fkEmpleado es requerido')
        if not data.get('fkSucursal'):
            errors.append('fkSucursal es requerido')
        return errors

    @staticmethod
    def validate_update(data):
        return []
