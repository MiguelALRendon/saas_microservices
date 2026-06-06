class BaseSchema:
    """Schema base con métodos comunes y helpers de escalabilidad.

    Los helpers de cache/batch/envelope son la base del patrón anti-N+1:
    - empty_cache(): crea un cache por-llamada (vive una sola operación schema).
    - prefetch_external(): hace get_by_oid_list en batch y lo mete al cache.
    - resolve_external(): lee del cache; si no está, cae a get_by_oid individual.
    - paginated_envelope(): envuelve un external.get_list() en el formato estándar.
    - paginate_local(): pagina un query SQLAlchemy interno con el mismo envelope.
    - paginate_junction_external(): pagina la junction local y resuelve el otro
      lado (externo) en batch — clave para detalle de empleado→sucursales, etc.
    """

    # ── Serialización base ──────────────────────────────────────────────────

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
    def serialize_base_contacto(obj):
        data = BaseSchema.serialize_base(obj)
        data.update({'telefono': obj.telefono, 'email': obj.email})
        return data

    # ── Cache por-llamada ───────────────────────────────────────────────────

    @staticmethod
    def empty_cache() -> dict:
        """Cache nuevo. Estructura: {key: {oid: payload}}."""
        return {}

    @staticmethod
    def prefetch_external(cache: dict, key: str, oids, external_class) -> None:
        """Resuelve en BATCH y popula el cache. 1 HTTP por external_class.

        Args:
            cache: dict creado por empty_cache().
            key: nombre semántico ('empresa', 'sistema', etc.).
            oids: iterable de OIDs (acepta None y duplicados).
            external_class: clase con get_by_oid_list().
        """
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
        """Lee del cache. Miss → get_by_oid individual (con write-through al cache)."""
        if not oid:
            return None
        bucket = cache.setdefault(key, {})
        if oid in bucket:
            return bucket[oid]
        item = external_class.get_by_oid(oid)
        if item is not None:
            bucket[oid] = item
        return item

    # ── Envelopes paginados ─────────────────────────────────────────────────

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
        """Llama external_class.get_list y normaliza al envelope estándar.

        Para colecciones hijas que viven en OTRO microservicio.
        """
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
        """Pagina un query SQLAlchemy interno y serializa la página actual.

        Para colecciones hijas que viven en el MISMO microservicio.
        """
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return BaseSchema._envelope(
            data=serialize_fn(pagination.items),
            total=pagination.total,
            page=pagination.page,
            per_page=pagination.per_page,
            pages=pagination.pages,
        )

    @staticmethod
    def paginate_junction_external(
        cache: dict,
        junction_query,
        fk_attr: str,
        cache_key: str,
        external_class,
        per_page: int = 25,
        page: int = 1,
    ) -> dict:
        """Pagina una junction interna y resuelve la otra punta vía external en batch.

        Caso de uso: empleado.empleado_sucursales (junction local en branch) →
        sucursales (externas en catalogues). Pagina las junctions, después batch-fetch
        SOLO las sucursales de esta página.
        """
        pagination = junction_query.paginate(page=page, per_page=per_page, error_out=False)
        oids = [getattr(j, fk_attr) for j in pagination.items if getattr(j, fk_attr)]
        BaseSchema.prefetch_external(cache, cache_key, oids, external_class)
        bucket = cache.get(cache_key, {})
        data = [bucket[getattr(j, fk_attr)] for j in pagination.items
                if getattr(j, fk_attr) and getattr(j, fk_attr) in bucket]
        return BaseSchema._envelope(
            data=data,
            total=pagination.total,
            page=pagination.page,
            per_page=pagination.per_page,
            pages=pagination.pages,
        )
