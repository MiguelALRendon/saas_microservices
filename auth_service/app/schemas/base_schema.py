class BaseSchema:
    """Schema base con métodos comunes"""
    
    @staticmethod
    def serialize_base(obj):
        """Serializa campos base de BaseObject"""
        return {
            'oid': obj.oid,
            'createdAt': obj.createdAt.isoformat() if obj.createdAt else None,
            'updatedAt': obj.updatedAt.isoformat() if obj.updatedAt else None,
            'creado_por': obj.creado_por,
            'editado_por': obj.editado_por,
            'estatus': obj.estatus.value if obj.estatus else None
        }
