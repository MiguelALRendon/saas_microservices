from app import db
from app.models.base import BaseObject


class EmpleadoSucursal(BaseObject):
    __tablename__ = 'empleado_sucursal'

    # FK interna — Empleado vive en este servicio
    fkEmpleado = db.Column(db.String(36), db.ForeignKey('empleado.oid'), nullable=False, index=True)

    # FK externa — Sucursal vive en catalogues_service
    fkSucursal = db.Column(db.String(36), nullable=False, index=True)

    # Relaciones
    empleado = db.relationship('Empleado', back_populates='empleado_sucursales')

    __table_args__ = (
        db.Index('ix_empleado_sucursal_unique', 'fkEmpleado', 'fkSucursal', unique=True),
    )

    def __repr__(self):
        return f'<EmpleadoSucursal Empleado:{self.fkEmpleado} - Sucursal:{self.fkSucursal}>'
