from app import db
from app.models.base import BaseObject

class VentaDetalle(BaseObject):
    __tablename__ = 'venta_detalle'
    
    cantidad = db.Column(db.Numeric(10, 2), nullable=False)
    precio_unitario_producto = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    descuento = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Foreign Keys - fkProducto referencia a otro microservicio
    fkVenta = db.Column(db.String(36), db.ForeignKey('venta.oid'), nullable=False, index=True)
    fkProducto = db.Column(db.String(36), nullable=False, index=True)
    
    # Relaciones
    venta = db.relationship('Venta', back_populates='detalles')
    
    def __repr__(self):
        return f'<VentaDetalle {self.oid}>'
