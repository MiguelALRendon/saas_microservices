from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config
from app.middleware import TrustedServiceMiddleware

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db, version_table='alembic_version_auth')
    jwt.init_app(app)

    # Registrar middleware de seguridad inter-servicio
    TrustedServiceMiddleware.register(app)
    
    # Importar modelos para que SQLAlchemy los registre
    with app.app_context():
        from app import models
    
    # Registrar blueprints
    from app.routes import usuario_bp, rol_bp, permiso_bp, permiso_asignado_bp, usuario_rol_bp
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(rol_bp)
    app.register_blueprint(permiso_bp)
    app.register_blueprint(permiso_asignado_bp)
    app.register_blueprint(usuario_rol_bp)
    
    return app
