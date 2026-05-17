from .base_schema import BaseSchema

class PermisoSchema(BaseSchema):
    """Schema para serialización y validación de Permiso"""
    
    @staticmethod
    def serialize(permiso):
        """Serializa un permiso a diccionario"""
        data = BaseSchema.serialize_base(permiso)
        data.update({
            'clave': permiso.clave,
            'nombre': permiso.nombre,
            'permiso': permiso.permiso
        })
        return data
    
    @staticmethod
    def serialize_list(permisos):
        """Serializa una lista de permisos"""
        return [PermisoSchema.serialize(permiso) for permiso in permisos]
    
    @staticmethod
    def validate_create(data):
        """Valida datos para crear un permiso"""
        errors = []
        
        if not data.get('clave'):
            errors.append('clave es requerida')
        if not data.get('nombre'):
            errors.append('nombre es requerido')
        if not data.get('permiso'):
            errors.append('permiso es requerido')
        
        return errors
    
    @staticmethod
    def validate_update(data):
        """Valida datos para actualizar un permiso"""
        # Para update, los campos no son obligatorios
        return []
