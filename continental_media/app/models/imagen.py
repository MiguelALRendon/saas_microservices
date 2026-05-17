from sqlalchemy import Column, String
from app.models.base import ContinentalBase


class Imagen(ContinentalBase):
    __tablename__ = 'imagenes'

    nombre = Column(String(255), nullable=False)
    url_archivo = Column(String(500), unique=True, nullable=False)

    def __repr__(self):
        return f'<Imagen {self.nombre}>'
