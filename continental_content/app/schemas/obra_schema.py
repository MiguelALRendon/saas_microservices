from .base_schema import BaseSchema


class ObraSchema(BaseSchema):

    @staticmethod
    def serialize(obra):
        data = BaseSchema.serialize_base(obra)
        data.update({
            'nombre': obra.nombre,
            'descripcion': obra.descripcion,
            'url_portada': obra.url_portada,
            'orden': obra.orden,
            'icono': obra.icono,
        })
        return data

    @staticmethod
    def serialize_list(obras):
        return [ObraSchema.serialize(o) for o in obras]

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('nombre'):
            errors.append('nombre es requerido')
        return errors

    @staticmethod
    def validate_update(data):
        return []
