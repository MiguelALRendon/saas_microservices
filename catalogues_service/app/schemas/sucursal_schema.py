# Migrado a galurensoft_core: serialización base vía serialize_audit y resolución de la
# colección externa (empleados del branch_service) vía paginated_external + ResourceClient.
from galurensoft_core.serialization import paginated_external, serialize_audit
from .empresa_schema import EmpresaSchema


class SucursalSchema:
    """Schema para serialización y validación de Sucursal."""

    @staticmethod
    def serialize(sucursal, _cache=None):
        data = serialize_audit(sucursal)
        data.update({
            'clave': sucursal.clave,
            'nombre': sucursal.nombre,
            'folio': sucursal.folio,
            'direccion': sucursal.direccion,
            'telefono': sucursal.telefono,
            'fkEmpresa': sucursal.fkEmpresa,
            'empresa': EmpresaSchema.serialize(sucursal.empresa, _cache=_cache) if sucursal.empresa else None,
        })
        return data

    @staticmethod
    def serialize_list(sucursales, _cache=None):
        return [SucursalSchema.serialize(s, _cache=_cache) for s in sucursales]

    @staticmethod
    def serialize_detail(sucursal, per_page: int = 25, _cache=None):
        """Detalle paginado: empleados (externo, vía /empleado/?fkSucursal=)."""
        from app.external_branch.empleado_external import empleado_client

        data = SucursalSchema.serialize(sucursal, _cache=_cache)
        data['empleados'] = paginated_external(
            empleado_client, per_page=per_page, fkSucursal=sucursal.oid,
        )
        return data

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('clave'):
            errors.append('clave es requerida')
        if not data.get('nombre'):
            errors.append('nombre es requerido')
        if not data.get('folio'):
            errors.append('folio es requerido')
        if not data.get('direccion'):
            errors.append('direccion es requerida')
        if not data.get('fkEmpresa'):
            errors.append('fkEmpresa es requerido')
        return errors

    @staticmethod
    def validate_update(data):
        return []
