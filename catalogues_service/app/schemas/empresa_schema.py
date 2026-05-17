from .base_schema import BaseSchema


class EmpresaSchema(BaseSchema):
    """Schema para serialización y validación de Empresa"""
    
    @staticmethod
    def serialize(empresa):
        """Serializa una empresa a diccionario"""
        data = BaseSchema.serialize_base(empresa)
        data.update({
            'clave': empresa.clave,
            'nombre': empresa.nombre,
            'folio': empresa.folio,
            'urlLogo': empresa.urlLogo,
            'direccion': empresa.direccion,
            'telefono': empresa.telefono,
            'email': empresa.email
        })
        return data
    
    @staticmethod
    def serialize_list(empresas):
        """Serializa una lista de empresas"""
        return [EmpresaSchema.serialize(empresa) for empresa in empresas]
    
    @staticmethod
    def validate_create(data):
        """Valida datos para crear una empresa"""
        errors = []
        
        if not data.get('clave'):
            errors.append('clave es requerida')
        if not data.get('nombre'):
            errors.append('nombre es requerido')
        if not data.get('folio'):
            errors.append('folio es requerido')
        if not data.get('urlLogo'):
            errors.append('urlLogo es requerido')
        if not data.get('direccion'):
            errors.append('direccion es requerida')
        
        return errors
    
    @staticmethod
    def validate_update(data):
        """Valida datos para actualizar una empresa"""
        # Para update, los campos no son obligatorios
        return []
