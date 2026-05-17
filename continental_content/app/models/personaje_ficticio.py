from sqlalchemy import Column, String, Text
from app.models.base import ContinentalBase


class PersonajeFicticio(ContinentalBase):
    __tablename__ = 'personajes_ficticios'

    nombre = Column(String(50), nullable=False)
    url_foto_perfil = Column(String(255))
    descripcion = Column(Text)

    def __repr__(self):
        return f'<PersonajeFicticio {self.nombre}>'
