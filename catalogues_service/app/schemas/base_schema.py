from datetime import datetime
from app.enums import BaseObjectEstatus


class BaseSchema:
    """Schema base para serialización de objetos"""
    
    @staticmethod
    def serialize_base(obj):
        """Serializa los campos base de un objeto"""
        return {
            'oid': obj.oid,
            'createdAt': obj.createdAt.isoformat() if obj.createdAt else None,
            'updatedAt': obj.updatedAt.isoformat() if obj.updatedAt else None,
            'creado_por': obj.creado_por,
            'editado_por': obj.editado_por,
            'estatus': obj.estatus.value if obj.estatus else None
        }
    
    @staticmethod
    def validate_estatus(estatus_value):
        """Valida que el estatus sea válido"""
        if estatus_value is None:
            return BaseObjectEstatus.ACTIVO
        
        if isinstance(estatus_value, str):
            try:
                return BaseObjectEstatus[estatus_value.upper()]
            except KeyError:
                raise ValueError(f"Estatus inválido: {estatus_value}")
        
        return estatus_value
