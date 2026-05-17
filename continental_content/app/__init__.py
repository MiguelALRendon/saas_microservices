from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    origins = [o.strip() for o in (Config.CORS_ORIGINS or '').split(',') if o.strip()]
    CORS(app, origins=origins, supports_credentials=True)

    # Registrar middleware de seguridad inter-servicio
    from app.middleware import TrustedServiceMiddleware
    TrustedServiceMiddleware.register(app)

    with app.app_context():
        from app import models  # noqa: F401

        from app.routes.obra_routes import obra_bp
        from app.routes.arco_routes import arco_bp
        from app.routes.capitulo_routes import capitulo_bp
        from app.routes.noticia_routes import noticia_bp
        from app.routes.personaje_ficticio_routes import personaje_ficticio_bp
        from app.routes.nota_routes import nota_bp
        from app.routes.fecha_routes import fecha_bp
        from app.routes.variable_sistema_routes import variable_sistema_bp

        app.register_blueprint(obra_bp)
        app.register_blueprint(arco_bp)
        app.register_blueprint(capitulo_bp)
        app.register_blueprint(noticia_bp)
        app.register_blueprint(personaje_ficticio_bp)
        app.register_blueprint(nota_bp)
        app.register_blueprint(fecha_bp)
        app.register_blueprint(variable_sistema_bp)

    return app
