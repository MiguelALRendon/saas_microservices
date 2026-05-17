import requests
from config import Config


class SucursalExternal:
    """Wrapper GET-only para Sucursal del catalogues_service.

    TODO: Deuda técnica - implementar create/update cuando se configure
          autenticación entre servicios (service tokens / API keys).
    """

    BASE_URL = Config.CATALOGUES_SERVICE_URL

    @staticmethod
    def _headers() -> dict:
        return {'X-Internal-Service-Secret': Config.INTERNAL_SERVICE_SECRET}

    @staticmethod
    def get_by_oid(oid: str) -> dict | None:
        """Obtiene una sucursal por su OID"""
        try:
            response = requests.get(f'{SucursalExternal.BASE_URL}/sucursal/{oid}', headers=SucursalExternal._headers())
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None

    @staticmethod
    def get_list(page: int = 1, per_page: int = 10, **filters) -> dict:
        """Obtiene el listado paginado de sucursales"""
        try:
            params = {'page': page, 'per_page': per_page, **filters}
            response = requests.get(f'{SucursalExternal.BASE_URL}/sucursal/', params=params, headers=SucursalExternal._headers())
            if response.status_code == 200:
                return response.json()
            return {'data': [], 'total': 0, 'page': page, 'per_page': per_page, 'pages': 0}
        except Exception:
            return {'data': [], 'total': 0, 'page': page, 'per_page': per_page, 'pages': 0}

    @staticmethod
    def get_by_oid_list(oid_list: list) -> list:
        """Obtiene una lista específica de sucursales por sus OIDs"""
        try:
            response = requests.post(
                f'{SucursalExternal.BASE_URL}/sucursal/list',
                json={'oid_list': oid_list},
                headers=SucursalExternal._headers()
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception:
            return []

    # TODO: Deuda técnica - habilitar cuando se configure autenticación entre servicios
    # @staticmethod
    # def create(data: dict) -> dict | None: ...
    #
    # @staticmethod
    # def update(oid: str, data: dict) -> dict | None: ...
