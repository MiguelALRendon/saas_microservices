# Registro de blueprints del BFF admin.
# Las 13 entidades proxy 1:1 se generan declarativamente con galurensoft_api_kit
# (antes: 13 archivos de rutas idénticos). auth_routes (login/logout) se registra aparte.
from config import Config
from galurensoft_api_kit.auth import auth_required, csrf_required
from galurensoft_api_kit.proxy import ProxyResource, build_proxy_blueprint
from galurensoft_api_kit.sanitizer import sanitize_payload
from app.routes.auth_routes import auth_bp
from app.utils.proxy import registry
from app.utils.session_store import store

# (nombre_blueprint, servicio_destino, path_en_servicio)
_RESOURCES = [
    ('usuario', 'auth', '/usuario'),
    ('rol', 'auth', '/rol'),
    ('permiso', 'auth', '/permiso'),
    ('permiso_asignado', 'auth', '/permiso-asignado'),
    ('usuario_rol', 'auth', '/usuario-rol'),
    ('usuario_empleado', 'auth', '/usuario-empleado'),
    ('usuario_sucursal', 'auth', '/usuario-sucursal'),
    ('sistema', 'catalogues', '/sistema'),
    ('empresa', 'catalogues', '/empresa'),
    ('sucursal', 'catalogues', '/sucursal'),
    ('cargo', 'branch', '/cargo'),
    ('empleado', 'branch', '/empleado'),
    ('empleado_sucursal', 'branch', '/empleado-sucursal'),
]


def register_blueprints(app):
    app.register_blueprint(auth_bp)

    _auth = auth_required(store)
    _csrf = csrf_required(store)
    for name, service, target in _RESOURCES:
        resource = ProxyResource(
            name=name,
            service=service,
            url_prefix=f"{Config.API_PREFIX}{target}",
            target_prefix=target,
        )
        app.register_blueprint(build_proxy_blueprint(
            resource, registry, auth=_auth, csrf=_csrf, sanitize=sanitize_payload,
        ))
