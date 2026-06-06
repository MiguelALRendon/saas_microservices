from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from app.middleware import TrustedServiceMiddleware

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db, version_table='alembic_version_branch')

    # Registrar middleware de seguridad inter-servicio
    TrustedServiceMiddleware.register(app)

    # Importar modelos para que SQLAlchemy los registre
    with app.app_context():
        from app import models

    # Registrar blueprints
    from app.routes import (
        cargo_bp,
        empleado_bp,
        turno_sucursal_bp,
        corte_caja_bp,
        empleado_sucursal_bp,
        turno_empleado_bp,
    )
    app.register_blueprint(cargo_bp)
    app.register_blueprint(empleado_bp)
    app.register_blueprint(turno_sucursal_bp)
    app.register_blueprint(corte_caja_bp)
    app.register_blueprint(empleado_sucursal_bp)
    app.register_blueprint(turno_empleado_bp)

    return app
