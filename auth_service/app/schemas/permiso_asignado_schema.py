from .base_schema import BaseSchema
from .permiso_schema import PermisoSchema
from .rol_schema import RolSchema


class PermisoAsignadoSchema(BaseSchema):
    """Junction Rol ↔ Permiso (con atributos crear/editar/desactivar/cancelar)."""

    @staticmethod
    def _serialize_attrs(pa) -> dict:
        data = BaseSchema.serialize_base(pa)
        data.update({
            'crear': pa.crear,
            'editar': pa.editar,
            'desactivar': pa.desactivar,
            'cancelar': pa.cancelar,
        })
        return data

    @staticmethod
    def serialize(pa, _cache=None):
        """Completa — ambos lados resueltos."""
        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        data = PermisoAsignadoSchema._serialize_attrs(pa)
        data['fkPermiso'] = pa.fkPermiso
        data['permiso'] = PermisoSchema.serialize(pa.permiso, _cache=cache) if pa.permiso else None
        data['fkRol'] = pa.fkRol
        data['rol'] = RolSchema.serialize(pa.rol, _cache=cache) if pa.rol else None
        return data

    @staticmethod
    def serialize_compact(pa, omit: str, _cache=None):
        """Compacta omitiendo un lado. omit ∈ {'permiso', 'rol'}."""
        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        data = PermisoAsignadoSchema._serialize_attrs(pa)
        if omit != 'permiso':
            data['fkPermiso'] = pa.fkPermiso
            data['permiso'] = PermisoSchema.serialize(pa.permiso, _cache=cache) if pa.permiso else None
        if omit != 'rol':
            data['fkRol'] = pa.fkRol
            data['rol'] = RolSchema.serialize(pa.rol, _cache=cache) if pa.rol else None
        return data

    @staticmethod
    def serialize_list(items, _cache=None):
        return [PermisoAsignadoSchema.serialize(pa, _cache=_cache) for pa in items]

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('fkPermiso'):
            errors.append('fkPermiso es requerido')
        if not data.get('fkRol'):
            errors.append('fkRol es requerido')
        return errors

    @staticmethod
    def validate_update(data):
        return []
