from flask import Flask
from config import Config
from app.middleware import TrustedServiceMiddleware


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Seguridad inter-servicio
    TrustedServiceMiddleware.register(app)

    # Registrar blueprints (proxy puro hacia los servicios dueños)
    from app.routes import (
        sistema_bp,
        empresa_bp,
        sucursal_bp,
        cargo_bp,
        empleado_bp,
        empleado_sucursal_bp,
        rol_bp,
        permiso_bp,
        permiso_asignado_bp,
        usuario_bp,
        usuario_rol_bp,
        usuario_empleado_bp,
        usuario_sucursal_bp,
    )

    for bp in (
        sistema_bp,
        empresa_bp,
        sucursal_bp,
        cargo_bp,
        empleado_bp,
        empleado_sucursal_bp,
        rol_bp,
        permiso_bp,
        permiso_asignado_bp,
        usuario_bp,
        usuario_rol_bp,
        usuario_empleado_bp,
        usuario_sucursal_bp,
    ):
        app.register_blueprint(bp)

    return app
