from .base_schema import BaseSchema
from .cargo_schema import CargoSchema
from app.enums import BaseObjectEstatus
from app.external_catalogues.empresa_external import EmpresaExternal
from app.external_catalogues.sucursal_external import SucursalExternal
from app.external_catalogues.sistema_external import SistemaExternal


class EmpleadoSchema(BaseSchema):
    """Schema para serialización y validación de Empleado."""

    @staticmethod
    def serialize(empleado, _cache=None):
        """Plana — usa cache pasado si lo hay (evita N+1 desde serialize_list)."""
        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        data = BaseSchema.serialize_base_contacto(empleado)
        data.update({
            'nombres': empleado.nombres,
            'apellido_paterno': empleado.apellido_paterno,
            'apellido_materno': empleado.apellido_materno,
            'curp': empleado.curp,
            'rfc': empleado.rfc,
            'fecha_contratacion': empleado.fecha_contratacion.isoformat() if empleado.fecha_contratacion else None,
            'fkCargo': empleado.fkCargo,
            'cargo': CargoSchema.serialize(empleado.cargo, _cache=cache) if empleado.cargo else None,
            'fkEmpresa': empleado.fkEmpresa,
            'empresa': BaseSchema.resolve_external(cache, 'empresa', empleado.fkEmpresa, EmpresaExternal),
            'fkSistema': empleado.fkSistema,
            'sistema': BaseSchema.resolve_external(cache, 'sistema', empleado.fkSistema, SistemaExternal),
        })
        return data

    @staticmethod
    def serialize_list(empleados, _cache=None):
        """Pre-batch de empresas y sistemas → 2 HTTPs totales sin importar N."""
        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        BaseSchema.prefetch_external(
            cache, 'empresa', [e.fkEmpresa for e in empleados], EmpresaExternal
        )
        BaseSchema.prefetch_external(
            cache, 'sistema', [e.fkSistema for e in empleados], SistemaExternal
        )
        return [EmpleadoSchema.serialize(e, _cache=cache) for e in empleados]

    @staticmethod
    def serialize_detail(empleado, per_page: int = 25, _cache=None):
        """Detalle paginado: sucursales (via junction local + external) y turnos (junction local)."""
        from .turno_empleado_schema import TurnoEmpleadoSchema
        from app.models.empleado_sucursal import EmpleadoSucursal
        from app.models.turno_empleado import TurnoEmpleado

        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        data = EmpleadoSchema.serialize(empleado, _cache=cache)

        # Sucursales: junction interna en branch + sucursal externa en catalogues
        sucursales_junction_q = empleado.empleado_sucursales.filter(
            EmpleadoSucursal.estatus == BaseObjectEstatus.ACTIVO
        )
        data['sucursales'] = BaseSchema.paginate_junction_external(
            cache=cache,
            junction_query=sucursales_junction_q,
            fk_attr='fkSucursal',
            cache_key='sucursal',
            external_class=SucursalExternal,
            per_page=per_page,
        )

        # Turno_empleados: junction interna entera; usamos compact omitiendo el lado 'empleado'
        turnos_junction_q = empleado.turno_empleados.filter(
            TurnoEmpleado.estatus == BaseObjectEstatus.ACTIVO
        )
        data['turno_empleados'] = BaseSchema.paginate_local(
            turnos_junction_q,
            lambda items: [
                TurnoEmpleadoSchema.serialize_compact(te, omit='empleado', _cache=cache)
                for te in items
            ],
            per_page=per_page,
        )
        return data

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('nombres'):
            errors.append('nombres es requerido')
        if not data.get('apellido_paterno'):
            errors.append('apellido_paterno es requerido')
        if not data.get('apellido_materno'):
            errors.append('apellido_materno es requerido')
        if not data.get('fecha_contratacion'):
            errors.append('fecha_contratacion es requerida')
        if not data.get('fkCargo'):
            errors.append('fkCargo es requerido')
        if not data.get('fkEmpresa'):
            errors.append('fkEmpresa es requerido')
        if not data.get('fkSistema'):
            errors.append('fkSistema es requerido')
        return errors

    @staticmethod
    def validate_update(data):
        return []
