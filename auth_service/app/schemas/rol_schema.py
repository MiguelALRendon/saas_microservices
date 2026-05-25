from .base_schema import BaseSchema

class RolSchema(BaseSchema):
    """Schema para serialización y validación de Rol"""
    
    @staticmethod
    def serialize(rol):
        """Serializa un rol a diccionario"""
        data = BaseSchema.serialize_base(rol)
        data.update({
            'nombre': rol.nombre,
            'fkSistema': rol.fkSistema,
            'fkEmpresa': rol.fkEmpresa,
        })
        return data
    
    @staticmethod
    def serialize_list(roles):
        """Serializa una lista de roles"""
        return [RolSchema.serialize(rol) for rol in roles]
    
    @staticmethod
    def validate_create(data):
        """Valida datos para crear un rol"""
        errors = []
        
        if not data.get('nombre'):
            errors.append('nombre es requerido')
        if not data.get('fkSistema'):
            errors.append('fkSistema es requerido')

        return errors
    
    @staticmethod
    def validate_update(data):
        """Valida datos para actualizar un rol"""
        # Para update, los campos no son obligatorios
        return []
