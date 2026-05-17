from app import db
from app.models.base import BaseObject

class ProveedorProducto(BaseObject):
    __tablename__ = 'proveedor_producto'
    
    # Foreign Keys - fkProducto referencia a otro microservicio
    fkProveedorEmpleado = db.Column(db.String(36), db.ForeignKey('proveedor_empleado.oid'), nullable=False, index=True)
    fkProducto = db.Column(db.String(36), nullable=False, index=True)
    fkProveedorMarca = db.Column(db.String(36), db.ForeignKey('proveedor_marca.oid'), nullable=False, index=True)
    
    # Relaciones
    proveedor_empleado = db.relationship('ProveedorEmpleado', back_populates='proveedor_productos')
    proveedor_marca = db.relationship('ProveedorMarca', back_populates='proveedor_productos')
    
    # Índices
    __table_args__ = (
        db.Index('ix_proveedor_producto_unique', 'fkProveedorEmpleado', 'fkProducto', 'fkProveedorMarca', unique=True),
    )
    
    def __repr__(self):
        return f'<ProveedorProducto Proveedor:{self.fkProveedorEmpleado} - Producto:{self.fkProducto} - Marca:{self.fkProveedorMarca}>'
