from app import db
from app.models.base import BaseObject

class Rol(BaseObject):
    __tablename__ = 'rol'
    
    nombre = db.Column(db.String(100), nullable=False, unique=True, index=True)
    
    # Relaciones
    usuario_roles = db.relationship('UsuarioRol', back_populates='rol', lazy='dynamic')
    permisos_asignados = db.relationship('PermisoAsignado', back_populates='rol', lazy='dynamic')
    
    def __repr__(self):
        return f'<Rol {self.nombre}>'
