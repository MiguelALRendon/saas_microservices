class BaseSchema:
    """Schema base para entidades ContinentalBase."""

    @staticmethod
    def serialize_base(obj):
        """Serializa campos base de ContinentalBase."""
        return {
            'id': obj.id,
            'created_at': obj.created_at.isoformat() if obj.created_at else None,
            'updated_at': obj.updated_at.isoformat() if obj.updated_at else None,
            'estatus': obj.estatus,
            'url_busqueda': obj.url_busqueda,
        }

    @staticmethod
    def serialize_concept_base(obj):
        """Serializa campos base de ConceptBase (sin estatus ni url_busqueda)."""
        return {
            'id': obj.id,
            'created_at': obj.created_at.isoformat() if obj.created_at else None,
            'updated_at': obj.updated_at.isoformat() if obj.updated_at else None,
        }

    @staticmethod
    def serialize_seo(obj):
        """Serializa campos SEO comunes."""
        return {
            'titulo_seo': obj.titulo_seo,
            'descripcion_seo': obj.descripcion_seo,
            'slug': obj.slug,
            'keywords': obj.keywords,
            'canonical_url': obj.canonical_url,
            'no_index': obj.no_index,
            'no_follow': obj.no_follow,
            'og_title': obj.og_title,
            'og_description': obj.og_description,
            'og_image': obj.og_image,
            'og_type': obj.og_type,
            'og_url': obj.og_url,
            'alt_text_image': obj.alt_text_image,
            'schema_type': obj.schema_type,
            'tags': obj.tags,
            'social_sharing_enabled': obj.social_sharing_enabled,
            'seo_score': obj.seo_score,
        }
