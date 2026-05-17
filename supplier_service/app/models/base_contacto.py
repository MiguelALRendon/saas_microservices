from app import db
from .base import BaseObject

class BaseContactoObject(BaseObject):
    __abstract__ = True
    
    telefono = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
