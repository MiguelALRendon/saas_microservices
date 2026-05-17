from .base_schema import BaseSchema


class UsuarioSchema(BaseSchema):

    @staticmethod
    def serialize(usuario):
        data = BaseSchema.serialize_base(usuario)
        data.update({
            'nombre': usuario.nombre,
        })
        return data

    @staticmethod
    def serialize_list(usuarios):
        return [UsuarioSchema.serialize(u) for u in usuarios]

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('nombre'):
            errors.append('nombre es requerido')
        if not data.get('contraseña'):
            errors.append('contraseña es requerida')
        if data.get('nombre') and len(data['nombre']) < 3:
            errors.append('nombre debe tener al menos 3 caracteres')
        if data.get('nombre') and len(data['nombre']) > 50:
            errors.append('nombre no puede superar 50 caracteres')
        if data.get('contraseña') and len(data['contraseña']) < 8:
            errors.append('contraseña debe tener al menos 8 caracteres')
        return errors

    @staticmethod
    def validate_update(data):
        errors = []
        if 'nombre' in data and data['nombre'] and len(data['nombre']) < 3:
            errors.append('nombre debe tener al menos 3 caracteres')
        if 'contraseña' in data and data['contraseña'] and len(data['contraseña']) < 8:
            errors.append('contraseña debe tener al menos 8 caracteres')
        return errors
