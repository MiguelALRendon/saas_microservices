from .base_schema import BaseSchema
from .usuario_schema import UsuarioSchema
from app.external_branch.empleado_external import EmpleadoExternal


class UsuarioEmpleadoSchema(BaseSchema):
    """Junction Usuario ↔ Empleado (Empleado vive en branch_service)."""

    @staticmethod
    def serialize(ue, _cache=None):
        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        data = BaseSchema.serialize_base(ue)
        data.update({
            'fkUsuario': ue.fkUsuario,
            'usuario': UsuarioSchema.serialize(ue.usuario, _cache=cache) if ue.usuario else None,
            'fkEmpleado': ue.fkEmpleado,
            'empleado': BaseSchema.resolve_external(cache, 'empleado', ue.fkEmpleado, EmpleadoExternal),
        })
        return data

    @staticmethod
    def serialize_compact(ue, omit: str, _cache=None):
        """omit ∈ {'usuario', 'empleado'}."""
        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        data = BaseSchema.serialize_base(ue)
        if omit != 'usuario':
            data['fkUsuario'] = ue.fkUsuario
            data['usuario'] = UsuarioSchema.serialize(ue.usuario, _cache=cache) if ue.usuario else None
        if omit != 'empleado':
            data['fkEmpleado'] = ue.fkEmpleado
            data['empleado'] = BaseSchema.resolve_external(cache, 'empleado', ue.fkEmpleado, EmpleadoExternal)
        return data

    @staticmethod
    def serialize_list(items, _cache=None):
        """Pre-batch de empleados (externos) y sistemas (vía usuarios)."""
        from app.external_catalogues.sistema_external import SistemaExternal

        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        usuarios = [ue.usuario for ue in items if ue.usuario]
        BaseSchema.prefetch_external(cache, 'sistema', [u.fkSistema for u in usuarios], SistemaExternal)
        BaseSchema.prefetch_external(cache, 'empleado', [ue.fkEmpleado for ue in items], EmpleadoExternal)
        return [UsuarioEmpleadoSchema.serialize(ue, _cache=cache) for ue in items]

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('fkUsuario'):
            errors.append('fkUsuario es requerido')
        if not data.get('fkEmpleado'):
            errors.append('fkEmpleado es requerido')
        return errors

    @staticmethod
    def validate_update(data):
        return []
