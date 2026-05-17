from app import db
from app.models.base import BaseObject
from app.enums import TipoCosto

class EntradaMercanciaDetalle(BaseObject):
    __tablename__ = 'entrada_mercancia_detalle'
    
    cantidad = db.Column(db.Numeric(10, 2), nullable=False)
    tipo_costo = db.Column(db.Enum(TipoCosto), nullable=False, index=True)
    costo_por_pieza = db.Column(db.Numeric(10, 2), nullable=False)
    descuento_por_pieza = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    descuento = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Foreign Keys - fkProducto referencia a otro microservicio
    fkEntradaMercancia = db.Column(db.String(36), db.ForeignKey('entrada_mercancia.oid'), nullable=False, index=True)
    fkProducto = db.Column(db.String(36), nullable=False, index=True)
    
    # Relaciones
    entrada_mercancia = db.relationship('EntradaMercancia', back_populates='detalles')
    
    def __repr__(self):
        return f'<EntradaMercanciaDetalle {self.oid}>'
