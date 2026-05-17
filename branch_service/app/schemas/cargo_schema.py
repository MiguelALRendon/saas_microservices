from .base_schema import BaseSchema


class CargoSchema(BaseSchema):
    """Schema para serialización y validación de Cargo"""

    @staticmethod
    def serialize(cargo):
        """Serializa un cargo a diccionario"""
        data = BaseSchema.serialize_base(cargo)
        data.update({
            'clave': cargo.clave,
            'nombre': cargo.nombre,
        })
        return data

    @staticmethod
    def serialize_list(cargos):
        """Serializa una lista de cargos"""
        return [CargoSchema.serialize(cargo) for cargo in cargos]

    @staticmethod
    def validate_create(data):
        """Valida datos para crear un cargo"""
        errors = []

        if not data.get('clave'):
            errors.append('clave es requerida')
        if not data.get('nombre'):
            errors.append('nombre es requerido')

        return errors

    @staticmethod
    def validate_update(data):
        """Valida datos para actualizar un cargo"""
        return []
