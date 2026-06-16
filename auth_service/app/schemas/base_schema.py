# Migrado a galurensoft_core: este BaseSchema ahora delega en la librería compartida,
# conservando la API estática que usan los schemas de entidad (serialize_base,
# empty_cache, prefetch_external, resolve_external, paginate_local, paginated_envelope,
# paginate_junction_external) — así los schemas no cambian.
from galurensoft_core.serialization import serialize_audit
from galurensoft_core.serialization import paginate_local as _paginate_local
from galurensoft_core.serialization import paginated_external as _paginated_external
from galurensoft_core.serialization import paginate_junction_external as _paginate_junction_external


class BaseSchema:
    @staticmethod
    def serialize_base(obj):
        return serialize_audit(obj)

    # ── cache por-llamada (dict { key: { oid: payload } }) ──────────────────────
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

    # ── envelopes (delegan en la librería) ──────────────────────────────────────
    @staticmethod
    def paginate_local(query, serialize_fn, per_page: int = 25, page: int = 1) -> dict:
        return _paginate_local(query, serialize_fn, page=page, per_page=per_page)

    @staticmethod
    def paginated_envelope(external_class, per_page: int = 25, page: int = 1, **filters) -> dict:
        return _paginated_external(external_class, page=page, per_page=per_page, **filters)

    @staticmethod
    def paginate_junction_external(cache, junction_query, fk_attr, cache_key, external_class,
                                   per_page: int = 25, page: int = 1) -> dict:
        return _paginate_junction_external(junction_query, fk_attr, external_class, page=page, per_page=per_page)
