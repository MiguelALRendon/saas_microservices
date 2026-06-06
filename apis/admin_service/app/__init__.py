# BFF público del panel admin (POS). Migrado a galurensoft_api_kit.gateway.create_gateway_app:
# JWT + CORS + handlers de error + registro de blueprints (login + proxies generados).
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
