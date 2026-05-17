import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-gateway-secret-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'dev-jwt-secret-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(weeks=int(os.environ.get('JWT_EXPIRES_WEEKS', 1)))

    HOST = os.environ.get('HOST') or '0.0.0.0'
    PORT = int(os.environ.get('PORT') or 8200)
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')

    CORS_ORIGINS = os.environ.get('CORS_ORIGINS') or 'http://localhost:5173,http://localhost:3000'
    API_PREFIX = os.environ.get('API_PREFIX') or '/api/continental'

    AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL') or 'http://localhost:8000'
    CONTINENTAL_CONTENT_URL = os.environ.get('CONTINENTAL_CONTENT_URL') or 'http://localhost:8101'
    CONTINENTAL_MEDIA_URL = os.environ.get('CONTINENTAL_MEDIA_URL') or 'http://localhost:8102'
    CONTINENTAL_UTILITIES_URL = os.environ.get('CONTINENTAL_UTILITIES_URL') or 'http://localhost:8103'

    # Internal Service Security
    INTERNAL_SERVICE_SECRET = os.environ.get('INTERNAL_SERVICE_SECRET') or 'dev-internal-secret'
