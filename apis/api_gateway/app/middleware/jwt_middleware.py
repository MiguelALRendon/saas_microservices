# Migrado a galurensoft_api_kit.auth.auth_required, configurado con el SessionStore del
# gateway. Se mantiene el nombre `gateway_auth_required` usado por todas las rutas.
from galurensoft_api_kit.auth import auth_required
from app.utils.session_store import store

gateway_auth_required = auth_required(store)
