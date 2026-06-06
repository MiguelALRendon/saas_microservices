from app import db
from app.models.base import BaseObject


class UsuarioEmpleado(BaseObject):
    __tablename__ = 'usuario_empleado'

    # FK interna — Usuario vive en este servicio
    fkUsuario = db.Column(db.String(36), db.ForeignKey('usuario.oid'), nullable=False, index=True)

    # FK externa — Empleado vive en branch_service
    fkEmpleado = db.Column(db.String(36), nullable=False, index=True)

    # Relación
    usuario = db.relationship('Usuario', back_populates='usuario_empleados')

    __table_args__ = (
        db.Index('ix_usuario_empleado_unique', 'fkUsuario', 'fkEmpleado', unique=True),
    )

    def __repr__(self):
        return f'<UsuarioEmpleado Usuario:{self.fkUsuario} - Empleado:{self.fkEmpleado}>'
