class BaseSchema:

    @staticmethod
    def serialize_base(obj):
        return {
            'id': obj.id,
            'created_at': obj.created_at.isoformat() if obj.created_at else None,
            'updated_at': obj.updated_at.isoformat() if obj.updated_at else None,
            'estatus': obj.estatus,
            'url_busqueda': obj.url_busqueda,
        }
