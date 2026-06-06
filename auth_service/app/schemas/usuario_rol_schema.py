from .base_schema import BaseSchema
from .usuario_schema import UsuarioSchema
from .rol_schema import RolSchema


class UsuarioRolSchema(BaseSchema):
    """Junction Usuario ↔ Rol."""

    @staticmethod
    def serialize(ur, _cache=None):
        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        data = BaseSchema.serialize_base(ur)
        data.update({
            'fkUsuario': ur.fkUsuario,
            'usuario': UsuarioSchema.serialize(ur.usuario, _cache=cache) if ur.usuario else None,
            'fkRol': ur.fkRol,
            'rol': RolSchema.serialize(ur.rol, _cache=cache) if ur.rol else None,
        })
        return data

    @staticmethod
    def serialize_compact(ur, omit: str, _cache=None):
        """omit ∈ {'usuario', 'rol'}."""
        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        data = BaseSchema.serialize_base(ur)
        if omit != 'usuario':
            data['fkUsuario'] = ur.fkUsuario
            data['usuario'] = UsuarioSchema.serialize(ur.usuario, _cache=cache) if ur.usuario else None
        if omit != 'rol':
            data['fkRol'] = ur.fkRol
            data['rol'] = RolSchema.serialize(ur.rol, _cache=cache) if ur.rol else None
        return data

    @staticmethod
    def serialize_list(items, _cache=None):
        """Pre-batch de sistemas (vía usuarios anidados)."""
        from app.external_catalogues.sistema_external import SistemaExternal

        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        usuarios = [ur.usuario for ur in items if ur.usuario]
        BaseSchema.prefetch_external(cache, 'sistema', [u.fkSistema for u in usuarios], SistemaExternal)
        return [UsuarioRolSchema.serialize(ur, _cache=cache) for ur in items]

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('fkUsuario'):
            errors.append('fkUsuario es requerido')
        if not data.get('fkRol'):
            errors.append('fkRol es requerido')
        return errors

    @staticmethod
    def validate_update(data):
        return []
