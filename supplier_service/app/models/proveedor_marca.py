from app import db
from app.models.base import BaseObject

class ProveedorMarca(BaseObject):
    __tablename__ = 'proveedor_marca'
    
    clave = db.Column(db.String(50), nullable=False, unique=True, index=True)
    nombre = db.Column(db.String(200), nullable=False, index=True)
    
    # Relaciones
    proveedor_productos = db.relationship('ProveedorProducto', back_populates='proveedor_marca')
    proveedor_empresas = db.relationship('ProveedorEmpresa', back_populates='proveedor_marca')
    
    def __repr__(self):
        return f'<ProveedorMarca {self.nombre}>'
