import re
import unicodedata
from app import db


def slugify(text: str) -> str:
    """Genera un slug URL-friendly desde texto, con soporte para español."""
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = text.lower().strip()
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'[^a-z0-9\-]', '', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    return text or 'sin-nombre'


def generate_unique_url_busqueda(base_text: str, model_class, exclude_id: str = None) -> str:
    """Genera un url_busqueda único para el modelo dado."""
    base_slug = slugify(base_text)
    slug = base_slug

    counter = 1
    while True:
        query = model_class.query.filter_by(url_busqueda=slug)
        if exclude_id:
            query = query.filter(model_class.id != exclude_id)
        if not query.first():
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1
