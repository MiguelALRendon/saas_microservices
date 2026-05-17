from app import db
from app.models.base import BaseObject

class CorteCaja(BaseObject):
    __tablename__ = 'corte_caja'
    
    fecha = db.Column(db.DateTime, nullable=False, index=True)
    monto_inicial = db.Column(db.Numeric(10, 2), nullable=False)
    monto_final = db.Column(db.Numeric(10, 2), nullable=False)
    esperado = db.Column(db.Numeric(10, 2), nullable=False)
    diferencia = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Foreign Keys - referencias a otros microservicios
    fkEmpresa = db.Column(db.String(36), nullable=False, index=True)
    fkSucursal = db.Column(db.String(36), nullable=False, index=True)
    fkUsuario = db.Column(db.String(36), nullable=False, index=True)
    fkTurno = db.Column(db.String(36), db.ForeignKey('turno_sucursal.oid'), nullable=False, index=True)
    fkSistema = db.Column(db.String(36), nullable=False, index=True)
    
    # Relaciones
    turno = db.relationship('TurnoSucursal', back_populates='cortes_caja')
    
    # Índices compuestos
    __table_args__ = (
        db.Index('ix_corte_caja_sucursal_fecha', 'fkSucursal', 'fecha'),
        db.Index('ix_corte_caja_usuario_fecha', 'fkUsuario', 'fecha'),
        db.Index('ix_corte_caja_turno_fecha', 'fkTurno', 'fecha'),
    )
    
    def __repr__(self):
        return f'<CorteCaja {self.oid}>'
