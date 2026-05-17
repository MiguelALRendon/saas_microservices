import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer
from app import db


class ContinentalBase(db.Model):
    __abstract__ = True

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    estatus = Column(Integer, default=1, nullable=False)
    url_busqueda = Column(String(255), nullable=False, unique=True)
