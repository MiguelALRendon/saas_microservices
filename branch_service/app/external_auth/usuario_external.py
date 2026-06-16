# Migrado a galurensoft_core.clients.ResourceClient.
from config import Config
from galurensoft_core.clients import RequestsTransport, ResourceClient

_client = ResourceClient(Config.AUTH_SERVICE_URL, 'usuario',
                         RequestsTransport(secret=Config.INTERNAL_SERVICE_SECRET))


class UsuarioExternal:
    @staticmethod
    def get_by_oid(oid):
        return _client.get_by_oid(oid)

    @staticmethod
    def get_list(page=1, per_page=10, **filters):
        return _client.get_list(page=page, per_page=per_page, **filters)

    @staticmethod
    def get_by_oid_list(oid_list):
        return _client.get_by_oid_list(oid_list)
