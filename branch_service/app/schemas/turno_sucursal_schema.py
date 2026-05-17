from .base_schema import BaseSchema
from app.external_catalogues.empresa_external import EmpresaExternal
from app.external_catalogues.sucursal_external import SucursalExternal


class TurnoSucursalSchema(BaseSchema):
    """Schema para serialización y validación de TurnoSucursal"""

    @staticmethod
    def serialize(turno):
        """Serializa un turno de sucursal a diccionario"""
        data = BaseSchema.serialize_base(turno)
        data.update({
            'nombre': turno.nombre,
            'hora_entrada': turno.hora_entrada.isoformat() if turno.hora_entrada else None,
            'hora_salida': turno.hora_salida.isoformat() if turno.hora_salida else None,
            'hora_corte': turno.hora_corte.isoformat() if turno.hora_corte else None,
            # FKs externas — catalogues_service
            'fkEmpresa': turno.fkEmpresa,
            'empresa': EmpresaExternal.get_by_oid(turno.fkEmpresa) if turno.fkEmpresa else None,
            'fkSucursal': turno.fkSucursal,
            'sucursal': SucursalExternal.get_by_oid(turno.fkSucursal) if turno.fkSucursal else None,
        })
        return data

    @staticmethod
    def serialize_list(turnos):
        """Serializa una lista de turnos"""
        return [TurnoSucursalSchema.serialize(turno) for turno in turnos]

    @staticmethod
    def validate_create(data):
        """Valida datos para crear un turno de sucursal"""
        errors = []

        if not data.get('nombre'):
            errors.append('nombre es requerido')
        if not data.get('hora_entrada'):
            errors.append('hora_entrada es requerida')
        if not data.get('hora_salida'):
            errors.append('hora_salida es requerida')
        if not data.get('hora_corte'):
            errors.append('hora_corte es requerida')
        if not data.get('fkEmpresa'):
            errors.append('fkEmpresa es requerido')
        if not data.get('fkSucursal'):
            errors.append('fkSucursal es requerido')

        return errors

    @staticmethod
    def validate_update(data):
        """Valida datos para actualizar un turno de sucursal"""
        return []
