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

    with app.app_context():
        from app import models

    return app
