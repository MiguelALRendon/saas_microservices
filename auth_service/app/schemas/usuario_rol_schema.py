from .base_schema import BaseSchema
from app.schemas.usuario_schema import UsuarioSchema
from app.schemas.rol_schema import RolSchema


class UsuarioRolSchema(BaseSchema):
    """Schema para serialización y validación de UsuarioRol"""

    @staticmethod
    def serialize(usuario_rol):
        """Serializa un usuario_rol a diccionario"""
        data = BaseSchema.serialize_base(usuario_rol)
        data.update({
            'fkUsuario': usuario_rol.fkUsuario,
            'usuario': UsuarioSchema.serialize(usuario_rol.usuario) if usuario_rol.usuario else None,
            'fkRol': usuario_rol.fkRol,
            'rol': RolSchema.serialize(usuario_rol.rol) if usuario_rol.rol else None,
        })
        return data
    
    @staticmethod
    def serialize_list(usuario_roles):
        """Serializa una lista de usuario_roles"""
        return [UsuarioRolSchema.serialize(ur) for ur in usuario_roles]
    
    @staticmethod
    def validate_create(data):
        """Valida datos para crear un usuario_rol"""
        errors = []
        
        if not data.get('fkUsuario'):
            errors.append('fkUsuario es requerido')
        if not data.get('fkRol'):
            errors.append('fkRol es requerido')
        
        return errors
    
    @staticmethod
    def validate_update(data):
        """Valida datos para actualizar un usuario_rol"""
        # Para update, los campos no son obligatorios
        return []
