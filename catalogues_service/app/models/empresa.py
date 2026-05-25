from app import db
from app.models.base_contacto import BaseContactoObject

class Empresa(BaseContactoObject):
    __tablename__ = 'empresa'

    clave = db.Column(db.String(50), nullable=False, index=True)
    nombre = db.Column(db.String(200), nullable=False, index=True)
    folio = db.Column(db.String(100), nullable=False)
    urlLogo = db.Column(db.String(500), nullable=False)
    direccion = db.Column(db.String(500), nullable=False)

    # FK externa — Sistema al que pertenece esta empresa
    fkSistema = db.Column(db.String(36), nullable=False, index=True)

    # Relación con Sucursales
    sucursales = db.relationship('Sucursal', back_populates='empresa', lazy='dynamic')

    # clave única dentro de cada sistema
    __table_args__ = (
        db.UniqueConstraint('clave', 'fkSistema', name='uq_empresa_clave_sistema'),
    )

    def __repr__(self):
        return f'<Empresa {self.nombre}>'
