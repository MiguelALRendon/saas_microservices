from app import db
from app.models.base_contacto import BaseContactoObject

class ProveedorEmpleado(BaseContactoObject):
    __tablename__ = 'proveedor_empleado'
    
    apellidoPaterno = db.Column(db.String(100), nullable=False, index=True)
    apellidoMaterno = db.Column(db.String(100), nullable=False)
    nombres = db.Column(db.String(200), nullable=False, index=True)
    
    # Relaciones
    proveedor_empresas = db.relationship('ProveedorEmpresa', back_populates='proveedor_empleado')
    proveedor_productos = db.relationship('ProveedorProducto', back_populates='proveedor_empleado')
    
    def __repr__(self):
        return f'<ProveedorEmpleado {self.nombres} {self.apellidoPaterno}>'
