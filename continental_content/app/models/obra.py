from sqlalchemy import Column, String, Text, Integer
from app.models.base import ContinentalBase


class Obra(ContinentalBase):
    __tablename__ = 'obras'

    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    url_portada = Column(String(255))
    orden = Column(Integer)
    icono = Column(String(40))

    def __repr__(self):
        return f'<Obra {self.nombre}>'
