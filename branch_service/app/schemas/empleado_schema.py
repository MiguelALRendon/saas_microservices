from .base_schema import BaseSchema
from .cargo_schema import CargoSchema
from app.external_catalogues.empresa_external import EmpresaExternal
from app.external_catalogues.sucursal_external import SucursalExternal


class EmpleadoSchema(BaseSchema):
    """Schema para serialización y validación de Empleado"""

    @staticmethod
    def serialize(empleado):
        """Serializa un empleado a diccionario"""
        data = BaseSchema.serialize_base_contacto(empleado)
        data.update({
            'nombres': empleado.nombres,
            'apellido_paterno': empleado.apellido_paterno,
            'apellido_materno': empleado.apellido_materno,
            'curp': empleado.curp,
            'rfc': empleado.rfc,
            'fecha_contratacion': empleado.fecha_contratacion.isoformat() if empleado.fecha_contratacion else None,
            # FK interna — Cargo
            'fkCargo': empleado.fkCargo,
            'cargo': CargoSchema.serialize(empleado.cargo) if empleado.cargo else None,
            # FKs externas — catalogues_service
            'fkEmpresa': empleado.fkEmpresa,
            'empresa': EmpresaExternal.get_by_oid(empleado.fkEmpresa) if empleado.fkEmpresa else None,
            'fkSucursal': empleado.fkSucursal,
            'sucursal': SucursalExternal.get_by_oid(empleado.fkSucursal) if empleado.fkSucursal else None,
        })
        return data

    @staticmethod
    def serialize_list(empleados):
        """Serializa una lista de empleados"""
        return [EmpleadoSchema.serialize(empleado) for empleado in empleados]

    @staticmethod
    def validate_create(data):
        """Valida datos para crear un empleado"""
        errors = []

        if not data.get('nombres'):
            errors.append('nombres es requerido')
        if not data.get('apellido_paterno'):
            errors.append('apellido_paterno es requerido')
        if not data.get('apellido_materno'):
            errors.append('apellido_materno es requerido')
        if not data.get('fecha_contratacion'):
            errors.append('fecha_contratacion es requerida')
        if not data.get('fkCargo'):
            errors.append('fkCargo es requerido')
        if not data.get('fkEmpresa'):
            errors.append('fkEmpresa es requerido')
        if not data.get('fkSucursal'):
            errors.append('fkSucursal es requerido')

        return errors

    @staticmethod
    def validate_update(data):
        """Valida datos para actualizar un empleado"""
        return []
