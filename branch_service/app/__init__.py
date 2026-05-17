from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from app.middleware import TrustedServiceMiddleware

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Registrar middleware de seguridad inter-servicio
    TrustedServiceMiddleware.register(app)

    # Importar modelos para que SQLAlchemy los registre
    with app.app_context():
        from app import models

    # Registrar blueprints
    from app.routes import cargo_bp, empleado_bp, turno_sucursal_bp, corte_caja_bp
    app.register_blueprint(cargo_bp)
    app.register_blueprint(empleado_bp)
    app.register_blueprint(turno_sucursal_bp)
    app.register_blueprint(corte_caja_bp)

    return app
