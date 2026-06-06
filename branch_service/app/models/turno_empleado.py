from app import db
from app.models.base import BaseObject
from app.enums import DiaSemana


class TurnoEmpleado(BaseObject):
    __tablename__ = 'turno_empleado'

    # FKs internas — ambos viven en este servicio
    fkTurnoSucursal = db.Column(db.String(36), db.ForeignKey('turno_sucursal.oid'), nullable=False, index=True)
    fkEmpleado = db.Column(db.String(36), db.ForeignKey('empleado.oid'), nullable=False, index=True)

    # Atributos del turno asignado
    diaSemana = db.Column(db.Enum(DiaSemana), nullable=False, index=True)
    fechaInicio = db.Column(db.Date, nullable=False)
    fechaFin = db.Column(db.Date, nullable=True)

    # Relaciones
    turno = db.relationship('TurnoSucursal', back_populates='turno_empleados')
    empleado = db.relationship('Empleado', back_populates='turno_empleados')

    __table_args__ = (
        db.Index(
            'ix_turno_empleado_unique',
            'fkTurnoSucursal', 'fkEmpleado', 'diaSemana', 'fechaInicio',
            unique=True,
        ),
    )

    def __repr__(self):
        return f'<TurnoEmpleado Turno:{self.fkTurnoSucursal} - Empleado:{self.fkEmpleado} - {self.diaSemana.value}>'
