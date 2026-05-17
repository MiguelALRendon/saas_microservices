from app.routes.auth_routes import auth_bp
from app.routes.usuario_routes import usuario_bp
from app.routes.rol_routes import rol_bp
from app.routes.permiso_routes import permiso_bp
from app.routes.permiso_asignado_routes import permiso_asignado_bp
from app.routes.usuario_rol_routes import usuario_rol_bp

__all__ = [
    'auth_bp',
    'usuario_bp',
    'rol_bp',
    'permiso_bp',
    'permiso_asignado_bp',
    'usuario_rol_bp',
]
