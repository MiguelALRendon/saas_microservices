from app import db
from app.models.base import BaseObject

class Rol(BaseObject):
    __tablename__ = 'rol'

    nombre = db.Column(db.String(100), nullable=False, index=True)

    # FKs externas — scope del rol
    fkSistema = db.Column(db.String(36), nullable=False, index=True)
    fkEmpresa = db.Column(db.String(36), nullable=True, index=True)  # nullable → rol global del sistema

    # Relaciones
    usuario_roles = db.relationship('UsuarioRol', back_populates='rol', lazy='dynamic')
    permisos_asignados = db.relationship('PermisoAsignado', back_populates='rol', lazy='dynamic')

    # nombre único por combinación sistema + empresa
    __table_args__ = (
        db.UniqueConstraint('nombre', 'fkSistema', 'fkEmpresa', name='uq_rol_nombre_sistema_empresa'),
    )

    def __repr__(self):
        return f'<Rol {self.nombre}>'
