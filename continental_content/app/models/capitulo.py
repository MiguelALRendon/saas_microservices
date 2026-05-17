from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import ContinentalBase, SeoMixin


class Capitulo(ContinentalBase, SeoMixin):
    __tablename__ = 'capitulos'

    titulo = Column(String(100), nullable=False)
    descripcion_larga = Column(Text)
    descripcion_corta = Column(String(160))
    url_portada = Column(String(255))
    texto_capitulo = Column(Text)
    comentario_creador = Column(Text)
    numero_capitulo = Column(Integer, nullable=False)
    subarco_id = Column(String(36), ForeignKey('arcos.id'))
    obra_id = Column(String(36), ForeignKey('obras.id'))

    subarco = relationship('Arco', backref='capitulos', foreign_keys=[subarco_id])
    obra = relationship('Obra', backref='capitulos', foreign_keys=[obra_id])

    def __repr__(self):
        return f'<Capitulo {self.titulo}>'
