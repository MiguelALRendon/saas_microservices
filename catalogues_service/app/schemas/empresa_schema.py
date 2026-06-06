# Migrado a galurensoft_core: serialize_audit + paginate_local (sucursales locales) +
# paginated_external (cargos del branch_service).
from galurensoft_core.serialization import paginate_local, paginated_external, serialize_audit


class EmpresaSchema:
    """Schema para serialización y validación de Empresa."""

    @staticmethod
    def serialize(empresa, _cache=None):
        data = serialize_audit(empresa)
        data.update({
            'clave': empresa.clave,
            'nombre': empresa.nombre,
            'folio': empresa.folio,
            'urlLogo': empresa.urlLogo,
            'direccion': empresa.direccion,
            'telefono': empresa.telefono,
            'email': empresa.email,
            'fkSistema': empresa.fkSistema,
        })
        return data

    @staticmethod
    def serialize_list(empresas, _cache=None):
        return [EmpresaSchema.serialize(e, _cache=_cache) for e in empresas]

    @staticmethod
    def serialize_detail(empresa, per_page: int = 25, _cache=None):
        """Detalle paginado: sucursales (local) + cargos (externo, branch_service)."""
        from app.enums import BaseObjectEstatus
        from app.models.sucursal import Sucursal
        from app.schemas.sucursal_schema import SucursalSchema
        from app.external_branch.cargo_external import cargo_client

        data = EmpresaSchema.serialize(empresa)

        sucursales_q = empresa.sucursales.filter(Sucursal.estatus == BaseObjectEstatus.ACTIVO)
        data['sucursales'] = paginate_local(
            sucursales_q, SucursalSchema.serialize_list, per_page=per_page,
        )
        data['cargos'] = paginated_external(
            cargo_client, per_page=per_page, fkEmpresa=empresa.oid,
        )
        return data

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('clave'):
            errors.append('clave es requerida')
        if not data.get('nombre'):
            errors.append('nombre es requerido')
        if not data.get('folio'):
            errors.append('folio es requerido')
        if not data.get('urlLogo'):
            errors.append('urlLogo es requerido')
        if not data.get('direccion'):
            errors.append('direccion es requerida')
        if not data.get('fkSistema'):
            errors.append('fkSistema es requerido')
        return errors

    @staticmethod
    def validate_update(data):
        return []
