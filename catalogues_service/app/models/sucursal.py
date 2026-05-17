from app import db
from app.models.base import BaseObject

class Sucursal(BaseObject):
    __tablename__ = 'sucursal'
    
    clave = db.Column(db.String(50), nullable=False, unique=True, index=True)
    nombre = db.Column(db.String(200), nullable=False, index=True)
    folio = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(500), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    
    # Foreign Key - referencia a empresa
    fkEmpresa = db.Column(db.String(36), db.ForeignKey('empresa.oid'), nullable=False, index=True)
    
    # Relación con Empresa
    empresa = db.relationship('Empresa', back_populates='sucursales')
    
    def __repr__(self):
        return f'<Sucursal {self.nombre}>'
