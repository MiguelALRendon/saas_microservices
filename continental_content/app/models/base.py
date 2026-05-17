import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Boolean, Float
from app import db


class ContinentalBase(db.Model):
    """Base para entidades principales que existen en continental_api_db.

    Nota: Usa 'id' (no 'oid'), 'created_at'/'updated_at' (no camelCase),
    y estatus Integer (1=ACTIVO, -1=INACTIVO) para mantener compatibilidad
    con el esquema DB existente de ContinentalApi.
    """
    __abstract__ = True

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    estatus = Column(Integer, default=1, nullable=False)  # 1=ACTIVO, -1=INACTIVO
    url_busqueda = Column(String(255), nullable=False, unique=True)


class ConceptBase(db.Model):
    """Base para entidades de concepto sin estatus ni url_busqueda."""
    __abstract__ = True

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)


class SeoMixin:
    """Mixin Python puro con campos SEO. No hereda de db.Model para
    compatibilidad con herencia múltiple en SQLAlchemy."""

    titulo_seo = Column(String(70))
    descripcion_seo = Column(String(160))
    slug = Column(String(200))
    keywords = Column(String(500))
    canonical_url = Column(String(500))
    no_index = Column(Boolean, default=False)
    no_follow = Column(Boolean, default=False)
    og_title = Column(String(70))
    og_description = Column(String(160))
    og_image = Column(String(500))
    og_type = Column(String(50))
    og_url = Column(String(500))
    alt_text_image = Column(String(500))
    schema_type = Column(String(50))
    tags = Column(String(500))
    social_sharing_enabled = Column(Boolean, default=True)
    seo_score = Column(Float)
