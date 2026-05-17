from .base_schema import BaseSchema
from .empresa_schema import EmpresaSchema


class SucursalSchema(BaseSchema):
    """Schema para serialización y validación de Sucursal"""
    
    @staticmethod
    def serialize(sucursal):
        """Serializa una sucursal a diccionario"""
        data = BaseSchema.serialize_base(sucursal)
        data.update({
            'clave': sucursal.clave,
            'nombre': sucursal.nombre,
            'folio': sucursal.folio,
            'direccion': sucursal.direccion,
            'telefono': sucursal.telefono,
            'fkEmpresa': sucursal.fkEmpresa,
            'empresa': EmpresaSchema.serialize(sucursal.empresa) if sucursal.empresa else None,
        })
        return data
    
    @staticmethod
    def serialize_list(sucursales):
        """Serializa una lista de sucursales"""
        return [SucursalSchema.serialize(sucursal) for sucursal in sucursales]
    
    @staticmethod
    def validate_create(data):
        """Valida datos para crear una sucursal"""
        errors = []
        
        if not data.get('clave'):
            errors.append('clave es requerida')
        if not data.get('nombre'):
            errors.append('nombre es requerido')
        if not data.get('folio'):
            errors.append('folio es requerido')
        if not data.get('direccion'):
            errors.append('direccion es requerida')
        if not data.get('fkEmpresa'):
            errors.append('fkEmpresa es requerido')
        
        return errors
    
    @staticmethod
    def validate_update(data):
        """Valida datos para actualizar una sucursal"""
        # Para update, los campos no son obligatorios
        return []
