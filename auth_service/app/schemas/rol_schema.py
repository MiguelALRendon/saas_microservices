from .base_schema import BaseSchema
from app.enums import BaseObjectEstatus


class RolSchema(BaseSchema):
    """Schema para serialización y validación de Rol."""

    @staticmethod
    def serialize(rol, _cache=None):
        """Plana."""
        data = BaseSchema.serialize_base(rol)
        data.update({
            'nombre': rol.nombre,
            'fkSistema': rol.fkSistema,
            'fkEmpresa': rol.fkEmpresa,
        })
        return data

    @staticmethod
    def serialize_list(roles, _cache=None):
        return [RolSchema.serialize(rol, _cache=_cache) for rol in roles]

    @staticmethod
    def serialize_detail(rol, per_page: int = 25, _cache=None):
        """Detalle paginado: permisos_asignados (junction interna)."""
        from .permiso_asignado_schema import PermisoAsignadoSchema
        from app.models.permiso_asignado import PermisoAsignado

        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        data = RolSchema.serialize(rol, _cache=cache)

        permisos_q = rol.permisos_asignados.filter(PermisoAsignado.estatus == BaseObjectEstatus.ACTIVO)
        data['permisos_asignados'] = BaseSchema.paginate_local(
            permisos_q,
            lambda items: [
                PermisoAsignadoSchema.serialize_compact(pa, omit='rol', _cache=cache)
                for pa in items
            ],
            per_page=per_page,
        )
        return data

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('nombre'):
            errors.append('nombre es requerido')
        if not data.get('fkSistema'):
            errors.append('fkSistema es requerido')
        return errors

    @staticmethod
    def validate_update(data):
        return []
