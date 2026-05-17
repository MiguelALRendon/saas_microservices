from .base_schema import BaseSchema


class SistemaSchema(BaseSchema):
    """Schema para serialización y validación de Sistema"""
    
    @staticmethod
    def serialize(sistema):
        """Serializa un sistema a diccionario"""
        data = BaseSchema.serialize_base(sistema)
        data.update({
            'clave': sistema.clave,
            'nombre': sistema.nombre,
            'descripcion': sistema.descripcion,
            'api_key': sistema.api_key
        })
        return data
    
    @staticmethod
    def serialize_list(sistemas):
        """Serializa una lista de sistemas"""
        return [SistemaSchema.serialize(sistema) for sistema in sistemas]
    
    @staticmethod
    def validate_create(data):
        """Valida datos para crear un sistema"""
        errors = []
        
        if not data.get('clave'):
            errors.append('clave es requerida')
        if not data.get('nombre'):
            errors.append('nombre es requerido')
        if not data.get('api_key'):
            errors.append('api_key es requerida')
        
        return errors
    
    @staticmethod
    def validate_update(data):
        """Valida datos para actualizar un sistema"""
        # Para update, los campos no son obligatorios
        return []
