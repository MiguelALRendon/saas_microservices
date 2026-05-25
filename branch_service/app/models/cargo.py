from app import db
from app.models.base import BaseObject


class Cargo(BaseObject):
    __tablename__ = 'cargo'

    clave = db.Column(db.String(25), nullable=False, index=True)
    nombre = db.Column(db.String(100), nullable=False)

    # FK externa — Empresa a la que pertenece este cargo
    fkEmpresa = db.Column(db.String(36), nullable=False, index=True)

    # Relaciones
    empleados = db.relationship('Empleado', back_populates='cargo')

    # clave única dentro de cada empresa
    __table_args__ = (
        db.UniqueConstraint('clave', 'fkEmpresa', name='uq_cargo_clave_empresa'),
    )

    def __repr__(self):
        return f'<Cargo {self.clave}>'
