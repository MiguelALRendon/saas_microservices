from app import db
from app.models.base import BaseObject

class Sistema(BaseObject):
    __tablename__ = 'sistema'

    clave = db.Column(db.String(50), nullable=False, unique=True, index=True)
    nombre = db.Column(db.String(200), nullable=False, index=True)
    descripcion = db.Column(db.Text, nullable=True)
    api_key = db.Column(db.String(255), nullable=False, unique=True)

    def __repr__(self):
        return f'<Sistema {self.clave} - {self.nombre}>'
