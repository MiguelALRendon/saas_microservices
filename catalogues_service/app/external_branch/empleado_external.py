# Migrado a galurensoft_core.clients.ResourceClient: el wrapper GET-only del branch_service
# ahora es un cliente parametrizable con transporte (secreto inter-servicio incluido).
# Se conserva la clase EmpleadoExternal con su API estática para compatibilidad.
from config import Config
from galurensoft_core.clients import RequestsTransport, ResourceClient

empleado_client = ResourceClient(
    Config.BRANCH_SERVICE_URL,
    'empleado',
    RequestsTransport(secret=Config.INTERNAL_SERVICE_SECRET),
)


class EmpleadoExternal:
    """Compat: API estática previa, ahora delegando en `empleado_client`."""

    @staticmethod
    def get_by_oid(oid: str):
        return empleado_client.get_by_oid(oid)

    @staticmethod
    def get_list(page: int = 1, per_page: int = 10, **filters):
        return empleado_client.get_list(page=page, per_page=per_page, **filters)

    @staticmethod
    def get_by_oid_list(oid_list: list):
        return empleado_client.get_by_oid_list(oid_list)
