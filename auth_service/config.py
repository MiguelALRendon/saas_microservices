import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'dev-jwt-secret-key'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Server Configuration
    HOST = os.environ.get('HOST') or '0.0.0.0'
    PORT = int(os.environ.get('PORT') or 8000)
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')
    BASE_URL = os.environ.get('BASE_URL') or f'http://localhost:{os.environ.get("PORT", 8000)}'
    
    # Microservices URLs
    AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL') or 'http://localhost:8000'
    CATALOGUES_SERVICE_URL = os.environ.get('CATALOGUES_SERVICE_URL') or 'http://localhost:8002'
    BRANCH_SERVICE_URL = os.environ.get('BRANCH_SERVICE_URL') or 'http://localhost:8001'
    INVENTORY_SERVICE_URL = os.environ.get('INVENTORY_SERVICE_URL') or 'http://localhost:8003'
    SALES_SERVICE_URL = os.environ.get('SALES_SERVICE_URL') or 'http://localhost:8004'
    SUPPLIER_SERVICE_URL = os.environ.get('SUPPLIER_SERVICE_URL') or 'http://localhost:8005'
    VALIDATION_SERVICE_URL = os.environ.get('VALIDATION_SERVICE_URL') or 'http://localhost:8006'

    # Internal Service Security
    INTERNAL_SERVICE_SECRET = os.environ.get('INTERNAL_SERVICE_SECRET') or 'dev-internal-secret'
