import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Server
    HOST = os.environ.get('HOST') or '0.0.0.0'
    PORT = int(os.environ.get('PORT') or 8101)
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')
    BASE_URL = os.environ.get('BASE_URL') or 'http://localhost:8101'

    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS') or 'http://localhost:5173,http://localhost:3000'

    # Cookies
    COOKIE_DOMAIN = os.environ.get('COOKIE_DOMAIN') or None

    # Continental Microservices URLs
    CONTINENTAL_CONTENT_URL = os.environ.get('CONTINENTAL_CONTENT_URL') or 'http://localhost:8101'
    CONTINENTAL_MEDIA_URL = os.environ.get('CONTINENTAL_MEDIA_URL') or 'http://localhost:8102'
    CONTINENTAL_UTILITIES_URL = os.environ.get('CONTINENTAL_UTILITIES_URL') or 'http://localhost:8103'

    # Internal Service Security
    INTERNAL_SERVICE_SECRET = os.environ.get('INTERNAL_SERVICE_SECRET') or 'dev-internal-secret'
