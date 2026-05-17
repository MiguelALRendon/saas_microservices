from .base_schema import BaseSchema
from app.enums import UnidadMedida


class ProductoSchema(BaseSchema):
    """Schema para serialización y validación de Producto"""
    
    @staticmethod
    def serialize(producto):
        """Serializa un producto a diccionario"""
        data = BaseSchema.serialize_base(producto)
        data.update({
            'clave': producto.clave,
            'nombre': producto.nombre,
            'codigo_barras': producto.codigo_barras,
            'unidadMedida': producto.unidadMedida.value if producto.unidadMedida else None,
            'is_especial': producto.is_especial,
            'fkProveedorMarca': producto.fkProveedorMarca
        })
        return data
    
    @staticmethod
    def serialize_list(productos):
        """Serializa una lista de productos"""
        return [ProductoSchema.serialize(producto) for producto in productos]
    
    @staticmethod
    def validate_create(data):
        """Valida datos para crear un producto"""
        errors = []
        
        if not data.get('clave'):
            errors.append('clave es requerida')
        if not data.get('nombre'):
            errors.append('nombre es requerido')
        if not data.get('unidadMedida'):
            errors.append('unidadMedida es requerida')
        else:
            # Validar que la unidad de medida sea válida
            try:
                if isinstance(data['unidadMedida'], str):
                    UnidadMedida[data['unidadMedida'].upper()]
            except KeyError:
                errors.append(f"unidadMedida inválida: {data['unidadMedida']}")
        
        if not data.get('fkProveedorMarca'):
            errors.append('fkProveedorMarca es requerido')
        
        return errors
    
    @staticmethod
    def validate_update(data):
        """Valida datos para actualizar un producto"""
        errors = []
        
        # Si se envía unidadMedida, validar que sea válida
        if 'unidadMedida' in data and data['unidadMedida']:
            try:
                if isinstance(data['unidadMedida'], str):
                    UnidadMedida[data['unidadMedida'].upper()]
            except KeyError:
                errors.append(f"unidadMedida inválida: {data['unidadMedida']}")
        
        return errors
