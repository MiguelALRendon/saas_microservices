# In-memory session store: jti → {auth_service_access_token, auth_service_refresh_token, csrf_token}
# For production, replace with Redis or a shared cache.
_store: dict = {}


def save_session(jti: str, auth_service_access_token: str, auth_service_refresh_token: str, csrf_token: str) -> None:
    _store[jti] = {
        'auth_service_access_token': auth_service_access_token,
        'auth_service_refresh_token': auth_service_refresh_token,
        'csrf_token': csrf_token,
    }


def get_session(jti: str) -> dict | None:
    return _store.get(jti)


def delete_session(jti: str) -> None:
    _store.pop(jti, None)
