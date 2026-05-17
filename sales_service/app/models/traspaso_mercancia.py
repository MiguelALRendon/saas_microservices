from app import db
from app.models.base import BaseObject
from app.enums import TipoTraspaso

class TraspasoMercancia(BaseObject):
    __tablename__ = 'traspaso_mercancia'
    
    fecha = db.Column(db.DateTime, nullable=False, index=True)
    tipo = db.Column(db.Enum(TipoTraspaso), nullable=False, index=True)
    observaciones = db.Column(db.Text, nullable=True)
    motivo = db.Column(db.String(500), nullable=True)
    
    # Foreign Keys - referencias a otros microservicios
    fkEmpresa = db.Column(db.String(36), nullable=False, index=True)
    fkSucursalOrigen = db.Column(db.String(36), nullable=False, index=True)
    fkSucursalDestino = db.Column(db.String(36), nullable=False, index=True)
    fkSistema = db.Column(db.String(36), nullable=False, index=True)
    
    # Relaciones
    detalles = db.relationship('TraspasoMercanciaDetalle', back_populates='traspaso_mercancia')
    
    # Índices
    __table_args__ = (
        db.Index('ix_traspaso_origen_fecha', 'fkSucursalOrigen', 'fecha'),
        db.Index('ix_traspaso_destino_fecha', 'fkSucursalDestino', 'fecha'),
    )
    
    def __repr__(self):
        return f'<TraspasoMercancia {self.oid}>'
