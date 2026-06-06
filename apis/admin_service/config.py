import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Server Configuration
    HOST = os.environ.get('HOST') or '0.0.0.0'
    PORT = int(os.environ.get('PORT') or 8010)
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')

    # URLs de los servicios dueños
    AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL') or 'http://localhost:8000'
    CATALOGUES_SERVICE_URL = os.environ.get('CATALOGUES_SERVICE_URL') or 'http://localhost:8002'
    BRANCH_SERVICE_URL = os.environ.get('BRANCH_SERVICE_URL') or 'http://localhost:8001'

    # Seguridad inter-servicio
    INTERNAL_SERVICE_SECRET = os.environ.get('INTERNAL_SERVICE_SECRET') or 'dev-internal-secret'
