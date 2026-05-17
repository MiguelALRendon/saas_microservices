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
    from app.routes import empresa_bp, producto_bp, sistema_bp, sucursal_bp
    app.register_blueprint(empresa_bp)
    app.register_blueprint(producto_bp)
    app.register_blueprint(sistema_bp)
    app.register_blueprint(sucursal_bp)
    
    return app
