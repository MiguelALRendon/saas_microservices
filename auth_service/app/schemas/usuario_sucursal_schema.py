from .base_schema import BaseSchema
from .usuario_schema import UsuarioSchema
from app.external_catalogues.sucursal_external import SucursalExternal


class UsuarioSucursalSchema(BaseSchema):
    """Junction Usuario ↔ Sucursal (Sucursal vive en catalogues_service)."""

    @staticmethod
    def serialize(us, _cache=None):
        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        data = BaseSchema.serialize_base(us)
        data.update({
            'fkUsuario': us.fkUsuario,
            'usuario': UsuarioSchema.serialize(us.usuario, _cache=cache) if us.usuario else None,
            'fkSucursal': us.fkSucursal,
            'sucursal': BaseSchema.resolve_external(cache, 'sucursal', us.fkSucursal, SucursalExternal),
        })
        return data

    @staticmethod
    def serialize_compact(us, omit: str, _cache=None):
        """omit ∈ {'usuario', 'sucursal'}."""
        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        data = BaseSchema.serialize_base(us)
        if omit != 'usuario':
            data['fkUsuario'] = us.fkUsuario
            data['usuario'] = UsuarioSchema.serialize(us.usuario, _cache=cache) if us.usuario else None
        if omit != 'sucursal':
            data['fkSucursal'] = us.fkSucursal
            data['sucursal'] = BaseSchema.resolve_external(cache, 'sucursal', us.fkSucursal, SucursalExternal)
        return data

    @staticmethod
    def serialize_list(items, _cache=None):
        """Pre-batch de sucursales (externas) y sistemas (vía usuarios)."""
        from app.external_catalogues.sistema_external import SistemaExternal

        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        usuarios = [us.usuario for us in items if us.usuario]
        BaseSchema.prefetch_external(cache, 'sistema', [u.fkSistema for u in usuarios], SistemaExternal)
        BaseSchema.prefetch_external(cache, 'sucursal', [us.fkSucursal for us in items], SucursalExternal)
        return [UsuarioSucursalSchema.serialize(us, _cache=cache) for us in items]

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('fkUsuario'):
            errors.append('fkUsuario es requerido')
        if not data.get('fkSucursal'):
            errors.append('fkSucursal es requerido')
        return errors

    @staticmethod
    def validate_update(data):
        return []
