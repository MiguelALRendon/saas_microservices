from flask import Blueprint
from app.middleware.jwt_middleware import gateway_auth_required
from app.middleware.csrf_middleware import csrf_required
from app.utils.proxy import proxy_to_utilities
from config import Config

deployment_bp = Blueprint('deployment', __name__, url_prefix=f"{Config.API_PREFIX}/deployment")


@deployment_bp.route('/reload-continental-page', methods=['POST'])
@gateway_auth_required
@csrf_required
def reload_continental_page():
    return proxy_to_utilities('/deployment/reload-continental-page')
