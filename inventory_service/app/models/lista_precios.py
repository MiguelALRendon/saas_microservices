from app import db
from app.models.base import BaseObject

class ListaPrecios(BaseObject):
    __tablename__ = 'lista_precios'
    
    # Foreign Keys - referencias a otros microservicios
    fkEmpresa = db.Column(db.String(36), nullable=False, index=True)
    fkSucursal = db.Column(db.String(36), nullable=False, index=True)
    fkProducto = db.Column(db.String(36), nullable=False, index=True)
    fkSistema = db.Column(db.String(36), nullable=False, index=True)
    
    # Precios
    precioVenta = db.Column(db.Numeric(10, 2), nullable=False)
    precioCompra = db.Column(db.Numeric(10, 2), nullable=False)
    precioMayoreo = db.Column(db.Numeric(10, 2), nullable=True)
    precioPromocion = db.Column(db.Numeric(10, 2), nullable=True)
    vigenciaPromocion = db.Column(db.DateTime, nullable=True, index=True)
    precio_modificado = db.Column(db.Boolean, nullable=False, default=False)
    
    # Índices
    __table_args__ = (
        db.Index('ix_lista_precios_sucursal_producto', 'fkSucursal', 'fkProducto', unique=True),
        db.Index('ix_lista_precios_promocion_vigente', 'vigenciaPromocion'),
        db.Index('ix_lista_precios_empresa', 'fkEmpresa'),
    )
    
    def __repr__(self):
        return f'<ListaPrecios Sucursal:{self.fkSucursal} - Producto:{self.fkProducto} - Venta:{self.precioVenta}>'
