# Migrado a galurensoft_core.web.create_service_app. Se conserva JWTManager (el login
# emite access/refresh tokens del auth_service).
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config
from galurensoft_core.web import create_service_app

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app():
    from app.routes import (
        auth_bp,
        usuario_bp,
        rol_bp,
        permiso_bp,
        permiso_asignado_bp,
        usuario_rol_bp,
        usuario_empleado_bp,
        usuario_sucursal_bp,
    )

    def on_models():
        from app import models  # noqa: F401

    app = create_service_app(
        config=Config,
        db=db,
        migrate=migrate,
        migrate_table='alembic_version_auth',
        blueprints=[
            auth_bp, usuario_bp, rol_bp, permiso_bp, permiso_asignado_bp,
            usuario_rol_bp, usuario_empleado_bp, usuario_sucursal_bp,
        ],
        on_models=on_models,
    )
    jwt.init_app(app)
    return app
