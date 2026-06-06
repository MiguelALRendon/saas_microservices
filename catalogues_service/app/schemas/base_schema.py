from app.enums import BaseObjectEstatus


class BaseSchema:
    """Schema base con métodos comunes y helpers de escalabilidad.

    Los helpers de cache/batch/envelope son la base del patrón anti-N+1:
    - empty_cache(): crea un cache por-llamada (vive una sola operación schema).
    - prefetch_external(): hace get_by_oid_list en batch y lo mete al cache.
    - resolve_external(): lee del cache; si no está, cae a get_by_oid individual.
    - paginated_envelope(): envuelve un external.get_list() en el formato estándar.
    - paginate_local(): pagina un query SQLAlchemy interno con el mismo envelope.
    """

    @staticmethod
    def serialize_base(obj):
        return {
            'oid': obj.oid,
            'createdAt': obj.createdAt.isoformat() if obj.createdAt else None,
            'updatedAt': obj.updatedAt.isoformat() if obj.updatedAt else None,
            'creado_por': obj.creado_por,
            'editado_por': obj.editado_por,
            'estatus': obj.estatus.value if obj.estatus else None,
        }

    @staticmethod
    def validate_estatus(estatus_value):
        if estatus_value is None:
            return BaseObjectEstatus.ACTIVO
        if isinstance(estatus_value, str):
            try:
                return BaseObjectEstatus[estatus_value.upper()]
            except KeyError:
                raise ValueError(f"Estatus inválido: {estatus_value}")
        return estatus_value

    @staticmethod
    def empty_cache() -> dict:
        return {}

    @staticmethod
    def prefetch_external(cache: dict, key: str, oids, external_class) -> None:
        bucket = cache.setdefault(key, {})
        unique_oids = {oid for oid in oids if oid}
        missing = [oid for oid in unique_oids if oid not in bucket]
        if not missing:
            return
        for item in external_class.get_by_oid_list(missing):
            if isinstance(item, dict) and item.get('oid'):
                bucket[item['oid']] = item

    @staticmethod
    def resolve_external(cache: dict, key: str, oid, external_class):
        if not oid:
            return None
        bucket = cache.setdefault(key, {})
        if oid in bucket:
            return bucket[oid]
        item = external_class.get_by_oid(oid)
        if item is not None:
            bucket[oid] = item
        return item

    @staticmethod
    def _envelope(data, total: int, page: int, per_page: int, pages: int) -> dict:
        return {
            'data': data,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': pages,
            'has_more': page < pages,
        }

    @staticmethod
    def paginated_envelope(external_class, per_page: int = 25, page: int = 1, **filters) -> dict:
        result = external_class.get_list(page=page, per_page=per_page, **filters)
        if not isinstance(result, dict):
            return BaseSchema._envelope([], 0, page, per_page, 0)
        return BaseSchema._envelope(
            data=result.get('data', []),
            total=result.get('total', 0),
            page=result.get('page', page),
            per_page=result.get('per_page', per_page),
            pages=result.get('pages', 0),
        )

    @staticmethod
    def paginate_local(query, serialize_fn, per_page: int = 25, page: int = 1) -> dict:
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return BaseSchema._envelope(
            data=serialize_fn(pagination.items),
            total=pagination.total,
            page=pagination.page,
            per_page=pagination.per_page,
            pages=pagination.pages,
        )
