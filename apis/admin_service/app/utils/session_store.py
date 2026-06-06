# Almacén de sesión del BFF (galurensoft_api_kit.sessions.MemorySessionStore).
# En producción: RedisSessionStore para escalar horizontalmente.
from galurensoft_api_kit.sessions import MemorySessionStore

store = MemorySessionStore()
_store = store._store  # alias al dict interno (compat con tests)


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
