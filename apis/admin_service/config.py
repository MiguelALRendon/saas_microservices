import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Security (BFF público: emite su propio JWT + CSRF de sesión)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-admin-secret-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'dev-jwt-secret-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(weeks=int(os.environ.get('JWT_EXPIRES_WEEKS', 1)))

    # Server Configuration
    HOST = os.environ.get('HOST') or '0.0.0.0'
    PORT = int(os.environ.get('PORT') or 8010)
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')

    CORS_ORIGINS = os.environ.get('CORS_ORIGINS') or 'http://localhost:5173,http://localhost:3000'
    API_PREFIX = os.environ.get('API_PREFIX') or '/api/admin'

    # URLs de los servicios dueños (POS)
    AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL') or 'http://localhost:8000'
    CATALOGUES_SERVICE_URL = os.environ.get('CATALOGUES_SERVICE_URL') or 'http://localhost:8002'
    BRANCH_SERVICE_URL = os.environ.get('BRANCH_SERVICE_URL') or 'http://localhost:8001'

    # Seguridad inter-servicio (admin_service es EMISOR del secreto hacia los servicios POS)
    INTERNAL_SERVICE_SECRET = os.environ.get('INTERNAL_SERVICE_SECRET') or 'dev-internal-secret'
