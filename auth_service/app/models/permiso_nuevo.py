from app import db
from app.models.base import BaseObject

class Permiso(BaseObject):
    __tablename__ = 'permisos'
    
    clave = db.Column(db.String(25), nullable=False, unique=True, index=True)
    nombre = db.Column(db.String(100), nullable=False, index=True)
    permiso = db.Column(db.String(100), nullable=False, index=True)
    
    # Relación con permisos asignados
    permisos_asignados = db.relationship('PermisoAsignado', back_populates='permiso', lazy='dynamic')
    
    def __repr__(self):
        return f'<Permiso {self.nombre} - {self.permiso}>'
