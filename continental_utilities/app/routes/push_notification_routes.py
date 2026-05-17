import os
import json
import base64
from datetime import datetime
from urllib.parse import urlparse
from flask import Blueprint, request, jsonify
from pywebpush import webpush, WebPushException
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from app import db
from app.models.push_subscription import PushSubscription

push_notification_bp = Blueprint('push_notification', __name__, url_prefix='/push-notification')


def _get_vapid_private_key():
    """Convierte la clave VAPID desde PEM o raw base64 URL-safe."""
    raw = os.environ.get('VAPID_PRIVATE_KEY')
    if not raw:
        return None

    if raw.startswith('-----BEGIN'):
        pem_key = raw.replace('\\n', '\n')
        private_key_obj = serialization.load_pem_private_key(
            pem_key.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        private_numbers = private_key_obj.private_numbers()
        return base64.urlsafe_b64encode(
            private_numbers.private_value.to_bytes(32, byteorder='big')
        ).decode('utf-8').rstrip('=')

    return raw


@push_notification_bp.route('/send', methods=['POST'])
def enviar_notificacion():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'errors': ['No se recibieron datos']}), 400

        for field in ['title', 'body']:
            if not data.get(field):
                return jsonify({'errors': [f'{field} es requerido']}), 400

        notification_payload = {
            'title': data.get('title'),
            'body': data.get('body'),
            'url': data.get('url', '/'),
            'icon': data.get('url_icon', '/default-icon.png'),
            'image': data.get('url_image'),
        }

        try:
            vapid_private_key = _get_vapid_private_key()
        except Exception as e:
            return jsonify({'errors': [f'Error al procesar clave VAPID: {str(e)}']}), 500

        vapid_public_key = os.environ.get('VAPID_PUBLIC_KEY')
        vapid_email = os.environ.get('VAPID_CLAIM_EMAIL', 'mailto:admin@galurian.com')

        if not vapid_private_key or not vapid_public_key:
            return jsonify({'errors': ['VAPID keys no configuradas']}), 500

        subscriptions = PushSubscription.query.all()
        total = len(subscriptions)
        sent, failed, removed = 0, 0, 0

        for sub in subscriptions:
            try:
                p256dh = sub.p256dh.strip()
                auth = sub.auth.strip()

                pad_p256dh = len(p256dh) % 4
                if pad_p256dh:
                    p256dh += '=' * (4 - pad_p256dh)

                pad_auth = len(auth) % 4
                if pad_auth:
                    auth += '=' * (4 - pad_auth)

                subscription_info = {
                    'endpoint': sub.endpoint,
                    'keys': {'p256dh': p256dh, 'auth': auth},
                }

                parsed_url = urlparse(sub.endpoint)
                endpoint_origin = f"{parsed_url.scheme}://{parsed_url.netloc}"

                vapid_claims = {
                    'sub': vapid_email,
                    'aud': endpoint_origin,
                }

                webpush(
                    subscription_info=subscription_info,
                    data=json.dumps(notification_payload),
                    vapid_private_key=vapid_private_key,
                    vapid_claims=vapid_claims,
                )

                sub.last_used = datetime.now()
                sent += 1

            except WebPushException as e:
                status_code = None
                if hasattr(e, 'response') and e.response:
                    status_code = e.response.status_code
                elif '410' in str(e) or '404' in str(e):
                    status_code = 410 if '410' in str(e) else 404

                if status_code in [404, 410]:
                    db.session.delete(sub)
                    removed += 1
                else:
                    failed += 1

            except Exception:
                failed += 1

        db.session.commit()

        return jsonify({
            'sent': sent,
            'failed': failed,
            'removed': removed,
            'total': total,
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500
