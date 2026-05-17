from sqlalchemy import Column, String, Text
from app.models.base import ContinentalBase


class VariableSistema(ContinentalBase):
    __tablename__ = 'variables_sistema'

    nombre = Column(String(100), nullable=False, unique=True)
    valor = Column(Text)

    def __repr__(self):
        return f'<VariableSistema {self.nombre}>'
