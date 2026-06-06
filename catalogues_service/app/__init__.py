from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from galurensoft_core.web import create_service_app

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    # Migrado a galurensoft_core.web.create_service_app: compone config + db + migrate +
    # middleware de confianza (lee INTERNAL_SERVICE_SECRET del config) + handlers de error
    # estándar + registro de blueprints.
    from app.routes import empresa_bp, producto_bp, sistema_bp, sucursal_bp

    def on_models():
        from app import models  # noqa: F401  registra los modelos en SQLAlchemy

    return create_service_app(
        config=Config,
        db=db,
        migrate=migrate,
        migrate_table='alembic_version_catalogues',
        blueprints=[empresa_bp, producto_bp, sistema_bp, sucursal_bp],
        on_models=on_models,
    )
