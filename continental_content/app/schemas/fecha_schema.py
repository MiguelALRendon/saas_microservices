from .base_schema import BaseSchema


class FechaSchema(BaseSchema):

    @staticmethod
    def serialize(fecha):
        data = BaseSchema.serialize_concept_base(fecha)
        data.update({
            'fecha': fecha.fecha.isoformat() if fecha.fecha else None,
            'evento': fecha.evento,
        })
        return data

    @staticmethod
    def serialize_list(fechas):
        return [FechaSchema.serialize(f) for f in fechas]

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('fecha'):
            errors.append('fecha es requerida')
        if not data.get('evento'):
            errors.append('evento es requerido')
        return errors

    @staticmethod
    def validate_update(data):
        return []
