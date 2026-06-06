# Migrado a galurensoft_api_kit.auth.csrf_required, configurado con el SessionStore del
# gateway. Se mantiene el nombre `csrf_required` usado por las rutas (compone DESPUÉS de
# gateway_auth_required).
from galurensoft_api_kit.auth import csrf_required as _csrf_required
from app.utils.session_store import store

csrf_required = _csrf_required(store)
