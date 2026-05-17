from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import ConceptBase


class Nota(ConceptBase):
    __tablename__ = 'notas'

    titulo_nota = Column(String(200), nullable=False)
    texto_nota = Column(Text, nullable=False)
    fk_obra = Column(String(36), ForeignKey('obras.id'), nullable=False)
    fk_arco = Column(String(36), ForeignKey('arcos.id'), nullable=True)

    obra = relationship('Obra', backref='notas', foreign_keys=[fk_obra])
    arco = relationship('Arco', backref='notas', foreign_keys=[fk_arco])

    def __repr__(self):
        return f'<Nota {self.titulo_nota}>'
