from app.models.base import BaseObject
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.permiso_nuevo import Permiso
from app.models.permiso_asignado import PermisoAsignado
from app.models.usuario_rol import UsuarioRol

__all__ = [
    'BaseObject',
    'Usuario',
    'Rol',
    'Permiso',
    'PermisoAsignado',
    'UsuarioRol',
]
