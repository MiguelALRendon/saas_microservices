from .base_schema import BaseSchema
from app.schemas.permiso_schema import PermisoSchema
from app.schemas.rol_schema import RolSchema


class PermisoAsignadoSchema(BaseSchema):
    """Schema para serialización y validación de PermisoAsignado"""

    @staticmethod
    def serialize(permiso_asignado):
        """Serializa un permiso asignado a diccionario"""
        data = BaseSchema.serialize_base(permiso_asignado)
        data.update({
            'fkPermiso': permiso_asignado.fkPermiso,
            'permiso': PermisoSchema.serialize(permiso_asignado.permiso) if permiso_asignado.permiso else None,
            'fkRol': permiso_asignado.fkRol,
            'rol': RolSchema.serialize(permiso_asignado.rol) if permiso_asignado.rol else None,
            'crear': permiso_asignado.crear,
            'editar': permiso_asignado.editar,
            'desactivar': permiso_asignado.desactivar,
            'cancelar': permiso_asignado.cancelar,
        })
        return data
    
    @staticmethod
    def serialize_list(permisos_asignados):
        """Serializa una lista de permisos asignados"""
        return [PermisoAsignadoSchema.serialize(pa) for pa in permisos_asignados]
    
    @staticmethod
    def validate_create(data):
        """Valida datos para crear un permiso asignado"""
        errors = []
        
        if not data.get('fkPermiso'):
            errors.append('fkPermiso es requerido')
        if not data.get('fkRol'):
            errors.append('fkRol es requerido')
        
        return errors
    
    @staticmethod
    def validate_update(data):
        """Valida datos para actualizar un permiso asignado"""
        # Para update, los campos no son obligatorios
        return []
