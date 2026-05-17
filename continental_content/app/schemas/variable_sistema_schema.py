from .base_schema import BaseSchema


class VariableSistemaSchema(BaseSchema):

    @staticmethod
    def serialize(variable):
        data = BaseSchema.serialize_base(variable)
        data.update({
            'nombre': variable.nombre,
            'valor': variable.valor,
        })
        return data

    @staticmethod
    def serialize_list(variables):
        return [VariableSistemaSchema.serialize(v) for v in variables]

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('nombre'):
            errors.append('nombre es requerido')
        return errors

    @staticmethod
    def validate_update(data):
        return []
