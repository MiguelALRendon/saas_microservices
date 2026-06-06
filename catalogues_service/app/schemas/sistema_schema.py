# Migrado a galurensoft_core: serialize_audit + paginate_local (empresas locales del sistema).
from galurensoft_core.serialization import paginate_local, serialize_audit


class SistemaSchema:
    """Schema para serialización y validación de Sistema."""

    @staticmethod
    def serialize(sistema, _cache=None):
        data = serialize_audit(sistema)
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
        """Detalle paginado: empresas del sistema (local)."""
        from app.enums import BaseObjectEstatus
        from app.models.empresa import Empresa
        from app.schemas.empresa_schema import EmpresaSchema

        data = SistemaSchema.serialize(sistema)
        empresas_q = Empresa.query.filter(
            Empresa.fkSistema == sistema.oid,
            Empresa.estatus == BaseObjectEstatus.ACTIVO,
        )
        data['empresas'] = paginate_local(
            empresas_q, EmpresaSchema.serialize_list, per_page=per_page,
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
