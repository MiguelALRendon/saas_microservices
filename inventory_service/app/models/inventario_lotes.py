from app import db
from app.models.base import BaseObject

class InventarioLotes(BaseObject):
    __tablename__ = 'inventario_lotes'
    
    # Foreign Keys - referencias a otros microservicios
    fkEmpresa = db.Column(db.String(36), nullable=False, index=True)
    fkSucursal = db.Column(db.String(36), nullable=False, index=True)
    fkProducto = db.Column(db.String(36), nullable=False, index=True)
    fkEntradaMercancia = db.Column(db.String(36), nullable=False, index=True)
    fkEntradaMercanciaDetalle = db.Column(db.String(36), nullable=False, index=True)
    
    # Atributos
    cantidad = db.Column(db.Integer, nullable=False, default=0)
    cantidadOriginal = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    
    # Índices
    __table_args__ = (
        db.Index('ix_inventario_lotes_sucursal_producto', 'fkSucursal', 'fkProducto'),
        db.Index('ix_inventario_lotes_empresa', 'fkEmpresa'),
    )
    
    def __repr__(self):
        return f'<InventarioLotes Sucursal:{self.fkSucursal} - Producto:{self.fkProducto} - Cantidad:{self.cantidad} - Precio:{self.precio}>'
