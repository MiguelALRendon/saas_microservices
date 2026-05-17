import uuid
from datetime import datetime
from app import db
from app.enums import BaseObjectEstatus

class BaseObject(db.Model):
    __abstract__ = True
    
    oid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    creado_por = db.Column(db.String(36), nullable=True)
    editado_por = db.Column(db.String(36), nullable=True)
    estatus = db.Column(db.Enum(BaseObjectEstatus), nullable=False, default=BaseObjectEstatus.ACTIVO)
