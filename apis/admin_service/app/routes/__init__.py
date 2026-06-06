from .sistema_routes import sistema_bp
from .empresa_routes import empresa_bp
from .sucursal_routes import sucursal_bp
from .cargo_routes import cargo_bp
from .empleado_routes import empleado_bp
from .empleado_sucursal_routes import empleado_sucursal_bp
from .rol_routes import rol_bp
from .permiso_routes import permiso_bp
from .permiso_asignado_routes import permiso_asignado_bp
from .usuario_routes import usuario_bp
from .usuario_rol_routes import usuario_rol_bp
from .usuario_empleado_routes import usuario_empleado_bp
from .usuario_sucursal_routes import usuario_sucursal_bp

__all__ = [
    'sistema_bp',
    'empresa_bp',
    'sucursal_bp',
    'cargo_bp',
    'empleado_bp',
    'empleado_sucursal_bp',
    'rol_bp',
    'permiso_bp',
    'permiso_asignado_bp',
    'usuario_bp',
    'usuario_rol_bp',
    'usuario_empleado_bp',
    'usuario_sucursal_bp',
]
