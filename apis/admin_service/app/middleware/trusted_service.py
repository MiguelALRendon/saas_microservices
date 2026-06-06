import secrets
from flask import request, jsonify, current_app


class TrustedServiceMiddleware:
    """
    Middleware que valida que toda petición entrante proviene de un microservicio
    o API autorizada mediante el header X-Internal-Service-Secret.

    Bloquea con 403 cualquier petición que no incluya el secreto correcto.
    """

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
