from .base_schema import BaseSchema
from app.enums import BaseObjectEstatus


class SistemaSchema(BaseSchema):
    """Schema para serialización y validación de Sistema."""

    @staticmethod
    def serialize(sistema, _cache=None):
        data = BaseSchema.serialize_base(sistema)
        data.update({
            'clave': sistema.clave,
            'nombre': sistema.nombre,
            'descripcion': sistema.descripcion,
            'api_key': sistema.api_key,
        })
        return data

    @staticmethod
    def serialize_list(sistemas, _cache=None):
        return [SistemaSchema.serialize(s, _cache=_cache) for s in sistemas]

    @staticmethod
    def serialize_detail(sistema, per_page: int = 25, _cache=None):
        """Detalle paginado: empresas del sistema (interno)."""
        from app.models.empresa import Empresa
        from .empresa_schema import EmpresaSchema

        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        data = SistemaSchema.serialize(sistema, _cache=cache)

        empresas_q = Empresa.query.filter(
            Empresa.fkSistema == sistema.oid,
            Empresa.estatus == BaseObjectEstatus.ACTIVO,
        )
        data['empresas'] = BaseSchema.paginate_local(
            empresas_q,
            lambda items: EmpresaSchema.serialize_list(items, _cache=cache),
            per_page=per_page,
        )
        return data

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('clave'):
            errors.append('clave es requerida')
        if not data.get('nombre'):
            errors.append('nombre es requerido')
        if not data.get('api_key'):
            errors.append('api_key es requerida')
        return errors

    @staticmethod
    def validate_update(data):
        return []
