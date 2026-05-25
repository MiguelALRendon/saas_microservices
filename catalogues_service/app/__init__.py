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
    migrate.init_app(app, db, version_table='alembic_version_catalogues')

    # Registrar middleware de seguridad inter-servicio
    TrustedServiceMiddleware.register(app)
    
    # Importar modelos para que SQLAlchemy los registre
    with app.app_context():
        from app import models
    
    # Registrar blueprints
    from app.routes import empresa_bp, producto_bp, sistema_bp, sucursal_bp
    app.register_blueprint(empresa_bp)
    app.register_blueprint(producto_bp)
    app.register_blueprint(sistema_bp)
    app.register_blueprint(sucursal_bp)
    
    return app
