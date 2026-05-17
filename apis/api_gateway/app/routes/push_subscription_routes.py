from flask import Blueprint, request
from app.middleware.jwt_middleware import gateway_auth_required
from app.middleware.csrf_middleware import csrf_required
from app.utils.sanitizer import sanitize_dict, sanitize_list
from app.utils.proxy import proxy_to_utilities
from config import Config

# Note: unauthenticated browser push-subscription POSTs go to a separate gateway.
# This gateway handles admin-side operations only (requires JWT auth).
push_subscription_bp = Blueprint('push_subscription', __name__, url_prefix=f"{Config.API_PREFIX}/push-subscription")


@push_subscription_bp.route('/', methods=['GET'])
@gateway_auth_required
def get_subscriptions():
    return proxy_to_utilities('/push-subscription/')


@push_subscription_bp.route('/<string:oid>', methods=['GET'])
@gateway_auth_required
def get_subscription(oid):
    return proxy_to_utilities(f'/push-subscription/{oid}')


@push_subscription_bp.route('/many', methods=['POST'])
@gateway_auth_required
@csrf_required
def create_many_subscriptions():
    data = request.get_json() or []
    return proxy_to_utilities('/push-subscription/many', sanitize_list(data) if isinstance(data, list) else data)


@push_subscription_bp.route('/<string:oid>', methods=['PUT'])
@gateway_auth_required
@csrf_required
def update_subscription(oid):
    data = request.get_json() or {}
    return proxy_to_utilities(f'/push-subscription/{oid}', sanitize_dict(data))


@push_subscription_bp.route('/many', methods=['PUT'])
@gateway_auth_required
@csrf_required
def update_many_subscriptions():
    data = request.get_json() or []
    return proxy_to_utilities('/push-subscription/many', sanitize_list(data) if isinstance(data, list) else data)


@push_subscription_bp.route('/<string:oid>', methods=['DELETE'])
@gateway_auth_required
@csrf_required
def delete_subscription(oid):
    return proxy_to_utilities(f'/push-subscription/{oid}')
