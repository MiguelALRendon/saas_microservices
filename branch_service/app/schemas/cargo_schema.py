from .base_schema import BaseSchema
from app.enums import BaseObjectEstatus


class CargoSchema(BaseSchema):
    """Schema para serialización y validación de Cargo."""

    @staticmethod
    def serialize(cargo, _cache=None):
        """Plana — sin junctions ni hijos resueltos."""
        data = BaseSchema.serialize_base(cargo)
        data.update({
            'clave': cargo.clave,
            'nombre': cargo.nombre,
            'fkEmpresa': cargo.fkEmpresa,
        })
        return data

    @staticmethod
    def serialize_list(cargos, _cache=None):
        # Cargo no tiene externals que cachear hoy. Mantenemos la firma para consistencia.
        return [CargoSchema.serialize(c, _cache=_cache) for c in cargos]

    @staticmethod
    def serialize_detail(cargo, per_page: int = 25, _cache=None):
        """Detalle con empleados paginados (interno, mismo servicio)."""
        from .empleado_schema import EmpleadoSchema
        from app.models.empleado import Empleado

        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        data = CargoSchema.serialize(cargo, _cache=cache)

        # Empleados internos vía relación: paginate_local
        empleados_q = cargo.empleados.filter(Empleado.estatus == BaseObjectEstatus.ACTIVO) \
            if hasattr(cargo.empleados, 'filter') else None
        if empleados_q is None:
            # 'empleados' es list (no dynamic) — paginar manualmente sería redundante;
            # serializar normal pero envolver en envelope.
            active = [e for e in cargo.empleados if e.estatus == BaseObjectEstatus.ACTIVO]
            total = len(active)
            page_items = active[:per_page]
            data['empleados'] = BaseSchema._envelope(
                data=EmpleadoSchema.serialize_list(page_items, _cache=cache),
                total=total, page=1, per_page=per_page,
                pages=(total + per_page - 1) // per_page if total else 0,
            )
        else:
            data['empleados'] = BaseSchema.paginate_local(
                empleados_q,
                lambda items: EmpleadoSchema.serialize_list(items, _cache=cache),
                per_page=per_page,
            )
        return data

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('clave'):
            errors.append('clave es requerida')
        if not data.get('nombre'):
            errors.append('nombre es requerido')
        if not data.get('fkEmpresa'):
            errors.append('fkEmpresa es requerido')
        return errors

    @staticmethod
    def validate_update(data):
        return []
