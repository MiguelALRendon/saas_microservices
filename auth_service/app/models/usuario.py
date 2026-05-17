from app import db
from app.models.base import BaseObject

class Usuario(BaseObject):
    __tablename__ = 'usuario'
    
    usuario = db.Column(db.String(100), nullable=False, unique=True, index=True)
    contraseña = db.Column(db.String(255), nullable=False)
    
    # Foreign Keys - referencias a otros microservicios
    fkSistema = db.Column(db.String(36), nullable=False, index=True)
    fkEmpleado = db.Column(db.String(36), nullable=False, index=True)
    
    # Relaciones
    usuario_roles = db.relationship('UsuarioRol', back_populates='usuario', lazy='dynamic')
    
    def __repr__(self):
        return f'<Usuario {self.usuario}>'
