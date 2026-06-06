# Migrado a galurensoft_api_kit.proxy (ProxyRegistry + passthrough). Se conservan las
# funciones proxy_to_* usadas por las rutas.
#
# NOTA: `import requests` se mantiene a propósito para que patch('app.utils.proxy.requests.request')
# de los tests existentes siga resolviendo; el passthrough de api_kit usa el mismo módulo global.
import requests  # noqa: F401
from config import Config
from galurensoft_api_kit.proxy import ProxyRegistry

_registry = ProxyRegistry(
    {
        'auth': Config.AUTH_SERVICE_URL,
        'content': Config.CONTINENTAL_CONTENT_URL,
        'media': Config.CONTINENTAL_MEDIA_URL,
        'utilities': Config.CONTINENTAL_UTILITIES_URL,
    },
    secret=Config.INTERNAL_SERVICE_SECRET,
)


def proxy_to_auth(path: str, json_data=None):
    return _registry.forward('auth', path, json_data=json_data)


def proxy_to_content(path: str, json_data=None):
    return _registry.forward('content', path, json_data=json_data)


def proxy_to_media(path: str, json_data=None, files=None, form_data=None):
    return _registry.forward('media', path, json_data=json_data, files=files, form_data=form_data)


def proxy_to_utilities(path: str, json_data=None):
    return _registry.forward('utilities', path, json_data=json_data)
