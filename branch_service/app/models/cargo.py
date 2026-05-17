from app import db
from app.models.base import BaseObject


class Cargo(BaseObject):
    __tablename__ = 'cargo'

    clave = db.Column(db.String(25), nullable=False, unique=True, index=True)
    nombre = db.Column(db.String(100), nullable=False)

    # Relaciones
    empleados = db.relationship('Empleado', back_populates='cargo')

    def __repr__(self):
        return f'<Cargo {self.clave}>'
