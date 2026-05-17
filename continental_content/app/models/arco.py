from sqlalchemy import Column, String, Integer, Boolean
from app.models.base import ContinentalBase


class Arco(ContinentalBase):
    __tablename__ = 'arcos'

    nombre = Column(String(50), nullable=False)
    es_subarco = Column(Boolean, default=False, nullable=False)
    orden = Column(Integer)

    def __repr__(self):
        return f'<Arco {self.nombre}>'
