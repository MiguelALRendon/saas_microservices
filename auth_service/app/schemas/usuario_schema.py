from .base_schema import BaseSchema
from app.external_catalogues.sistema_external import SistemaExternal
from app.external_branch.empleado_external import EmpleadoExternal


class UsuarioSchema(BaseSchema):
    """Schema para serialización y validación de Usuario"""

    @staticmethod
    def serialize(usuario):
        """Serializa un usuario a diccionario"""
        data = BaseSchema.serialize_base(usuario)
        data.update({
            'usuario': usuario.usuario,
            'fkSistema': usuario.fkSistema,
            'sistema': SistemaExternal.get_by_oid(usuario.fkSistema) if usuario.fkSistema else None,
            'fkEmpleado': usuario.fkEmpleado,
            'empleado': EmpleadoExternal.get_by_oid(usuario.fkEmpleado) if usuario.fkEmpleado else None,
        })
        # No incluir contraseña en la serialización
        return data
    
    @staticmethod
    def serialize_list(usuarios):
        """Serializa una lista de usuarios"""
        return [UsuarioSchema.serialize(usuario) for usuario in usuarios]
    
    @staticmethod
    def validate_create(data):
        """Valida datos para crear un usuario"""
        errors = []
        
        if not data.get('usuario'):
            errors.append('usuario es requerido')
        if not data.get('contraseña'):
            errors.append('contraseña es requerida')
        if not data.get('fkSistema'):
            errors.append('fkSistema es requerido')
        if not data.get('fkEmpleado'):
            errors.append('fkEmpleado es requerido')
        
        return errors
    
    @staticmethod
    def validate_update(data):
        """Valida datos para actualizar un usuario"""
        # Para update, los campos no son obligatorios
        return []
