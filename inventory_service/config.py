import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Internal Service Security
    INTERNAL_SERVICE_SECRET = os.environ.get('INTERNAL_SERVICE_SECRET') or 'dev-internal-secret'
