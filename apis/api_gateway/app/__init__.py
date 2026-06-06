# Migrado a galurensoft_api_kit.gateway.create_gateway_app: compone Flask + JWTManager +
# CORS + handlers de error estándar + registro de blueprints.
from config import Config
from galurensoft_api_kit.gateway import create_gateway_app


def create_app():
    from app.routes import register_blueprints

    return create_gateway_app(
        config=Config,
        blueprints=register_blueprints,
        cors_origins=Config.CORS_ORIGINS,
        cors_resources=f"{Config.API_PREFIX}/*",
    )
