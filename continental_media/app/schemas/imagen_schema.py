from .base_schema import BaseSchema


class ImagenSchema(BaseSchema):

    @staticmethod
    def serialize(imagen):
        data = BaseSchema.serialize_base(imagen)
        data.update({
            'nombre': imagen.nombre,
            'url_archivo': imagen.url_archivo,
        })
        return data

    @staticmethod
    def serialize_list(imagenes):
        return [ImagenSchema.serialize(i) for i in imagenes]

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('nombre'):
            errors.append('nombre es requerido')
        return errors

    @staticmethod
    def validate_update(data):
        return []
