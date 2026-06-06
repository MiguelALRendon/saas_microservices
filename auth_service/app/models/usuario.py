from app import db
from app.models.base import BaseObject


class Usuario(BaseObject):
    __tablename__ = 'usuario'

    usuario = db.Column(db.String(100), nullable=False, unique=True, index=True)
    contraseña = db.Column(db.String(255), nullable=False)

    # FK externa — Sistema al que pertenece este usuario (multi-tenant discriminator)
    fkSistema = db.Column(db.String(36), nullable=False, index=True)

    # Relaciones — vínculos a otras entidades vía junctions
    usuario_roles = db.relationship('UsuarioRol', back_populates='usuario', lazy='dynamic')
    usuario_empleados = db.relationship('UsuarioEmpleado', back_populates='usuario', lazy='dynamic')
    usuario_sucursales = db.relationship('UsuarioSucursal', back_populates='usuario', lazy='dynamic')

    def __repr__(self):
        return f'<Usuario {self.usuario}>'
