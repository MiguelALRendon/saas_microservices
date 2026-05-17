from .base_schema import BaseSchema


class PersonajeFicticioSchema(BaseSchema):

    @staticmethod
    def serialize(personaje):
        data = BaseSchema.serialize_base(personaje)
        data.update({
            'nombre': personaje.nombre,
            'url_foto_perfil': personaje.url_foto_perfil,
            'descripcion': personaje.descripcion,
        })
        return data

    @staticmethod
    def serialize_list(personajes):
        return [PersonajeFicticioSchema.serialize(p) for p in personajes]

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('nombre'):
            errors.append('nombre es requerido')
        return errors

    @staticmethod
    def validate_update(data):
        return []
