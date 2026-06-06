# Migrado a galurensoft_core.clients.ResourceClient (wrapper GET-only sobre branch_service/cargo).
from config import Config
from galurensoft_core.clients import RequestsTransport, ResourceClient

cargo_client = ResourceClient(
    Config.BRANCH_SERVICE_URL,
    'cargo',
    RequestsTransport(secret=Config.INTERNAL_SERVICE_SECRET),
)


class CargoExternal:
    """Compat: API estática previa, ahora delegando en `cargo_client`."""

    @staticmethod
    def get_by_oid(oid: str):
        return cargo_client.get_by_oid(oid)

    @staticmethod
    def get_list(page: int = 1, per_page: int = 10, **filters):
        return cargo_client.get_list(page=page, per_page=per_page, **filters)

    @staticmethod
    def get_by_oid_list(oid_list: list):
        return cargo_client.get_by_oid_list(oid_list)
