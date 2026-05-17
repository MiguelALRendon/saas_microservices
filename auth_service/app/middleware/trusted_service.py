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
        """
        Verifica el header de autenticación inter-servicio.
        Retorna (dict_error, status_code) si hay error, o (None, None) si es válido.
        Usa secrets.compare_digest para evitar timing attacks.
        """
        token = request.headers.get(TrustedServiceMiddleware.HEADER_NAME, '')
        expected = current_app.config.get('INTERNAL_SERVICE_SECRET', '')

        if not token or not secrets.compare_digest(token, expected):
            return {'errors': ['Acceso no autorizado']}, 403

        return None, None

    @staticmethod
    def register(app):
        """
        Registra el middleware como before_request en la aplicación Flask.
        Llamar desde create_app() después de inicializar extensiones.
        """
        @app.before_request
        def check_internal_secret():
            error, status = TrustedServiceMiddleware.validate()
            if error:
                return jsonify(error), status
