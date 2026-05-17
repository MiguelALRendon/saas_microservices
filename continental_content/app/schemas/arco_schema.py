from .base_schema import BaseSchema


class ArcoSchema(BaseSchema):

    @staticmethod
    def serialize(arco):
        data = BaseSchema.serialize_base(arco)
        data.update({
            'nombre': arco.nombre,
            'es_subarco': arco.es_subarco,
            'orden': arco.orden,
        })
        return data

    @staticmethod
    def serialize_list(arcos):
        return [ArcoSchema.serialize(a) for a in arcos]

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('nombre'):
            errors.append('nombre es requerido')
        return errors

    @staticmethod
    def validate_update(data):
        return []
