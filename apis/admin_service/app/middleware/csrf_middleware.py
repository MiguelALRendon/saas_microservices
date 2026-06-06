# csrf_required del BFF (galurensoft_api_kit.auth) configurado con el SessionStore.
from galurensoft_api_kit.auth import csrf_required as _csrf_required
from app.utils.session_store import store

csrf_required = _csrf_required(store)
