from .base_schema import BaseSchema
from app.enums import BaseObjectEstatus


class EmpresaSchema(BaseSchema):
    """Schema para serialización y validación de Empresa."""

    @staticmethod
    def serialize(empresa, _cache=None):
        data = BaseSchema.serialize_base(empresa)
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
        """Detalle paginado:
        - sucursales (interno, vía relationship)
        - cargos (externo, vía external_branch)
        """
        from .sucursal_schema import SucursalSchema
        from app.models.sucursal import Sucursal
        from app.external_branch.cargo_external import CargoExternal

        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        data = EmpresaSchema.serialize(empresa, _cache=cache)

        sucursales_q = empresa.sucursales.filter(Sucursal.estatus == BaseObjectEstatus.ACTIVO)
        data['sucursales'] = BaseSchema.paginate_local(
            sucursales_q,
            lambda items: SucursalSchema.serialize_list(items, _cache=cache),
            per_page=per_page,
        )

        data['cargos'] = BaseSchema.paginated_envelope(
            CargoExternal, per_page=per_page, fkEmpresa=empresa.oid,
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
