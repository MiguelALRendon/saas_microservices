from flask import Blueprint, request
from app.middleware.jwt_middleware import gateway_auth_required
from app.middleware.csrf_middleware import csrf_required
from app.utils.sanitizer import sanitize_dict
from app.utils.proxy import proxy_to_utilities
from config import Config

push_notification_bp = Blueprint('push_notification', __name__, url_prefix=f"{Config.API_PREFIX}/push-notification")


@push_notification_bp.route('/send', methods=['POST'])
@gateway_auth_required
@csrf_required
def send_notification():
    data = request.get_json() or {}
    return proxy_to_utilities('/push-notification/send', sanitize_dict(data))
