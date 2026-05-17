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

        from app.routes.push_subscription_routes import push_subscription_bp
        from app.routes.push_notification_routes import push_notification_bp
        from app.routes.deployment_routes import deployment_bp

        app.register_blueprint(push_subscription_bp)
        app.register_blueprint(push_notification_bp)
        app.register_blueprint(deployment_bp)

    return app
