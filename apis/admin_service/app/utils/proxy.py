# Proxy hacia los servicios POS (galurensoft_api_kit.proxy.ProxyRegistry).
# `import requests` se mantiene para que patch('app.utils.proxy.requests.request') de los
# tests resuelva (el passthrough de api_kit usa el mismo módulo global).
import requests  # noqa: F401
from config import Config
from galurensoft_api_kit.proxy import ProxyRegistry

registry = ProxyRegistry(
    {
        'auth': Config.AUTH_SERVICE_URL,
        'catalogues': Config.CATALOGUES_SERVICE_URL,
        'branch': Config.BRANCH_SERVICE_URL,
    },
    secret=Config.INTERNAL_SERVICE_SECRET,
)


# Compat: funciones proxy_to_* (por si algún código las usa).
def proxy_to_auth(path: str, json_data=None):
    return registry.forward('auth', path, json_data=json_data)


def proxy_to_catalogues(path: str, json_data=None):
    return registry.forward('catalogues', path, json_data=json_data)


def proxy_to_branch(path: str, json_data=None):
    return registry.forward('branch', path, json_data=json_data)
