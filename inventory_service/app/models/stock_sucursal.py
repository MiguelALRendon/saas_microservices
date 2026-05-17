from app import db
from app.models.base import BaseObject

class StockSucursal(BaseObject):
    __tablename__ = 'stock_sucursal'
    
    # Foreign Keys - referencias a otros microservicios
    fkEmpresa = db.Column(db.String(36), nullable=False, index=True)
    fkSucursal = db.Column(db.String(36), nullable=False, index=True)
    fkProducto = db.Column(db.String(36), nullable=False, index=True)
    
    # Atributos
    cantidad = db.Column(db.Integer, nullable=False, default=0)
    
    # Índices
    __table_args__ = (
        db.Index('ix_stock_sucursal_producto', 'fkSucursal', 'fkProducto', unique=True),
        db.Index('ix_stock_empresa', 'fkEmpresa'),
    )
    
    def __repr__(self):
        return f'<StockSucursal Sucursal:{self.fkSucursal} - Producto:{self.fkProducto} - Cantidad:{self.cantidad}>'
