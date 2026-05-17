from app import db
from app.models.base import BaseObject

class TraspasoMercanciaDetalle(BaseObject):
    __tablename__ = 'traspaso_mercancia_detalle'
    
    cantidad = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Foreign Keys - fkProducto referencia a otro microservicio
    fkTraspasoMercancia = db.Column(db.String(36), db.ForeignKey('traspaso_mercancia.oid'), nullable=False, index=True)
    fkProducto = db.Column(db.String(36), nullable=False, index=True)
    
    # Relaciones
    traspaso_mercancia = db.relationship('TraspasoMercancia', back_populates='detalles')
    
    def __repr__(self):
        return f'<TraspasoMercanciaDetalle {self.oid}>'
