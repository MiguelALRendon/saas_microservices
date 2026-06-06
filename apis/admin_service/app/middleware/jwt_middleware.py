# auth_required del BFF (galurensoft_api_kit.auth) configurado con el SessionStore.
from galurensoft_api_kit.auth import auth_required
from app.utils.session_store import store

gateway_auth_required = auth_required(store)
