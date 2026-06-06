from app import db
from app.models.base import BaseObject


class UsuarioSucursal(BaseObject):
    __tablename__ = 'usuario_sucursal'

    # FK interna — Usuario vive en este servicio
    fkUsuario = db.Column(db.String(36), db.ForeignKey('usuario.oid'), nullable=False, index=True)

    # FK externa — Sucursal vive en catalogues_service
    fkSucursal = db.Column(db.String(36), nullable=False, index=True)

    # Relación
    usuario = db.relationship('Usuario', back_populates='usuario_sucursales')

    __table_args__ = (
        db.Index('ix_usuario_sucursal_unique', 'fkUsuario', 'fkSucursal', unique=True),
    )

    def __repr__(self):
        return f'<UsuarioSucursal Usuario:{self.fkUsuario} - Sucursal:{self.fkSucursal}>'
