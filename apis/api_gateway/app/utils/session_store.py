# Migrado a galurensoft_api_kit.sessions.MemorySessionStore (puerto + adapter).
# En producción: cambiar por RedisSessionStore para escalar horizontalmente.
#
# Se conserva la API de funciones (save_session/get_session/delete_session) y el alias
# `_store` al dict interno para no romper código ni tests que lo inspeccionan.
from galurensoft_api_kit.sessions import MemorySessionStore

store = MemorySessionStore()
_store = store._store  # alias al dict interno (compat con tests existentes)


def save_session(jti: str, auth_service_access_token: str, auth_service_refresh_token: str, csrf_token: str) -> None:
    store.save(jti, {
        'auth_service_access_token': auth_service_access_token,
        'auth_service_refresh_token': auth_service_refresh_token,
        'csrf_token': csrf_token,
    })


def get_session(jti: str) -> dict | None:
    return store.get(jti)


def delete_session(jti: str) -> None:
    store.delete(jti)
