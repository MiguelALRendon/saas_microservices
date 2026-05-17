from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import ContinentalBase, SeoMixin


class Noticia(ContinentalBase, SeoMixin):
    __tablename__ = 'noticias'

    titulo = Column(String(100), nullable=False)
    descripcion_larga = Column(Text)
    descripcion_corta = Column(String(160))
    url_portada = Column(String(255))
    texto_noticia = Column(Text)
    autor_id = Column(String(36), ForeignKey('personajes_ficticios.id'))

    autor = relationship('PersonajeFicticio', backref='noticias', foreign_keys=[autor_id])

    def __repr__(self):
        return f'<Noticia {self.titulo}>'
