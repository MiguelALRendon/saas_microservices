from app import db
from app.models.base import BaseObject
from app.enums import UnidadMedida

class Producto(BaseObject):
    __tablename__ = 'producto'
    
    clave = db.Column(db.String(50), nullable=False, unique=True, index=True)
    nombre = db.Column(db.String(200), nullable=False, index=True)
    codigo_barras = db.Column(db.String(100), nullable=True, unique=True, index=True)
    unidadMedida = db.Column(db.Enum(UnidadMedida), nullable=False)
    is_especial = db.Column(db.Boolean, nullable=False, default=False)
    
    fkProveedorMarca = db.Column(db.String(36), nullable=False, index=True)
    
    def __repr__(self):
        return f'<Producto {self.nombre}>'
