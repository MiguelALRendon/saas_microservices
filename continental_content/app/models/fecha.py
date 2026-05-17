from sqlalchemy import Column, String, Date
from app.models.base import ConceptBase


class Fecha(ConceptBase):
    __tablename__ = 'fechas'

    fecha = Column(Date, nullable=False)
    evento = Column(String(255), nullable=False)

    def __repr__(self):
        return f'<Fecha {self.evento}>'
