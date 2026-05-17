from .base_schema import BaseSchema
from .turno_sucursal_schema import TurnoSucursalSchema
from app.external_catalogues.empresa_external import EmpresaExternal
from app.external_catalogues.sucursal_external import SucursalExternal
from app.external_catalogues.sistema_external import SistemaExternal
from app.external_auth.usuario_external import UsuarioExternal


class CorteCajaSchema(BaseSchema):
    """Schema para serialización y validación de CorteCaja"""

    @staticmethod
    def serialize(corte):
        """Serializa un corte de caja a diccionario"""
        data = BaseSchema.serialize_base(corte)
        data.update({
            'fecha': corte.fecha.isoformat() if corte.fecha else None,
            'monto_inicial': float(corte.monto_inicial) if corte.monto_inicial is not None else None,
            'monto_final': float(corte.monto_final) if corte.monto_final is not None else None,
            'esperado': float(corte.esperado) if corte.esperado is not None else None,
            'diferencia': float(corte.diferencia) if corte.diferencia is not None else None,
            # FK interna — TurnoSucursal
            'fkTurno': corte.fkTurno,
            'turno': TurnoSucursalSchema.serialize(corte.turno) if corte.turno else None,
            # FKs externas — catalogues_service
            'fkEmpresa': corte.fkEmpresa,
            'empresa': EmpresaExternal.get_by_oid(corte.fkEmpresa) if corte.fkEmpresa else None,
            'fkSucursal': corte.fkSucursal,
            'sucursal': SucursalExternal.get_by_oid(corte.fkSucursal) if corte.fkSucursal else None,
            'fkSistema': corte.fkSistema,
            'sistema': SistemaExternal.get_by_oid(corte.fkSistema) if corte.fkSistema else None,
            # FK externa — auth_service
            'fkUsuario': corte.fkUsuario,
            'usuario': UsuarioExternal.get_by_oid(corte.fkUsuario) if corte.fkUsuario else None,
        })
        return data

    @staticmethod
    def serialize_list(cortes):
        """Serializa una lista de cortes de caja"""
        return [CorteCajaSchema.serialize(corte) for corte in cortes]

    @staticmethod
    def validate_create(data):
        """Valida datos para crear un corte de caja"""
        errors = []

        if data.get('fecha') is None:
            errors.append('fecha es requerida')
        if data.get('monto_inicial') is None:
            errors.append('monto_inicial es requerido')
        if data.get('monto_final') is None:
            errors.append('monto_final es requerido')
        if data.get('esperado') is None:
            errors.append('esperado es requerido')
        if data.get('diferencia') is None:
            errors.append('diferencia es requerida')
        if not data.get('fkEmpresa'):
            errors.append('fkEmpresa es requerido')
        if not data.get('fkSucursal'):
            errors.append('fkSucursal es requerido')
        if not data.get('fkUsuario'):
            errors.append('fkUsuario es requerido')
        if not data.get('fkTurno'):
            errors.append('fkTurno es requerido')
        if not data.get('fkSistema'):
            errors.append('fkSistema es requerido')

        return errors

    @staticmethod
    def validate_update(data):
        """Valida datos para actualizar un corte de caja"""
        return []
