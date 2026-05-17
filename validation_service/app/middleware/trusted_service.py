import secrets
from flask import request, jsonify, current_app


class TrustedServiceMiddleware:
    HEADER_NAME = 'X-Internal-Service-Secret'

    @staticmethod
    def validate():
        token = request.headers.get(TrustedServiceMiddleware.HEADER_NAME, '')
        expected = current_app.config.get('INTERNAL_SERVICE_SECRET', '')

        if not token or not secrets.compare_digest(token, expected):
            return {'errors': ['Acceso no autorizado']}, 403

        return None, None

    @staticmethod
    def register(app):
        @app.before_request
        def check_internal_secret():
            error, status = TrustedServiceMiddleware.validate()
            if error:
                return jsonify(error), status
