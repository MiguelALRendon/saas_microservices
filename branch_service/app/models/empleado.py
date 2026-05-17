from app import db
from app.models.base_contacto import BaseContactoObject


class Empleado(BaseContactoObject):
    __tablename__ = 'empleado'

    nombres = db.Column(db.String(200), nullable=False)
    apellido_paterno = db.Column(db.String(100), nullable=False)
    apellido_materno = db.Column(db.String(100), nullable=False)
    curp = db.Column(db.String(18), nullable=True, unique=True, index=True)
    rfc = db.Column(db.String(13), nullable=True, index=True)
    fecha_contratacion = db.Column(db.Date, nullable=False)

    # FK interna — Cargo (dentro del mismo servicio)
    fkCargo = db.Column(db.String(36), db.ForeignKey('cargo.oid'), nullable=False, index=True)

    # FKs externas — referencias a otros microservicios
    fkEmpresa = db.Column(db.String(36), nullable=False, index=True)
    fkSucursal = db.Column(db.String(36), nullable=False, index=True)

    # Relaciones
    cargo = db.relationship('Cargo', back_populates='empleados')

    # Índices compuestos
    __table_args__ = (
        db.Index('ix_empleado_empresa_sucursal', 'fkEmpresa', 'fkSucursal'),
    )

    def __repr__(self):
        return f'<Empleado {self.apellido_paterno} {self.nombres}>'
