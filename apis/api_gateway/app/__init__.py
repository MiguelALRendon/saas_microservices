from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    jwt.init_app(app)
    CORS(
        app,
        resources={f"{Config.API_PREFIX}/*": {'origins': Config.CORS_ORIGINS.split(',')}},
        supports_credentials=True,
    )

    from app.routes import register_blueprints
    register_blueprints(app)

    return app
