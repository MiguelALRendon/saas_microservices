from .base_schema import BaseSchema


class PermisoSchema(BaseSchema):
    """Schema para serialización y validación de Permiso."""

    @staticmethod
    def serialize(permiso, _cache=None):
        data = BaseSchema.serialize_base(permiso)
        data.update({
            'clave': permiso.clave,
            'nombre': permiso.nombre,
            'permiso': permiso.permiso,
            'fkSistema': permiso.fkSistema,
        })
        return data

    @staticmethod
    def serialize_list(permisos, _cache=None):
        return [PermisoSchema.serialize(p, _cache=_cache) for p in permisos]

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('clave'):
            errors.append('clave es requerida')
        if not data.get('nombre'):
            errors.append('nombre es requerido')
        if not data.get('permiso'):
            errors.append('permiso es requerido')
        if not data.get('fkSistema'):
            errors.append('fkSistema es requerido')
        return errors

    @staticmethod
    def validate_update(data):
        return []
