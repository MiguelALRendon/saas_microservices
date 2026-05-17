import re
import uuid


def slugify(text: str) -> str:
    """Genera un slug URL-friendly a partir de texto."""
    slug = text.lower().strip()
    replacements = {
        'á': 'a', 'à': 'a', 'ä': 'a', 'â': 'a',
        'é': 'e', 'è': 'e', 'ë': 'e', 'ê': 'e',
        'í': 'i', 'ì': 'i', 'ï': 'i', 'î': 'i',
        'ó': 'o', 'ò': 'o', 'ö': 'o', 'ô': 'o',
        'ú': 'u', 'ù': 'u', 'ü': 'u', 'û': 'u',
        'ñ': 'n', 'ç': 'c',
    }
    for char, replacement in replacements.items():
        slug = slug.replace(char, replacement)
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def generate_unique_url_busqueda(base_text: str, model_class, exclude_id: str = None) -> str:
    """Genera un url_busqueda único para el modelo dado."""
    base_slug = slugify(base_text)
    if not base_slug:
        base_slug = str(uuid.uuid4())[:8]

    slug = base_slug
    counter = 1
    while True:
        query = model_class.query.filter_by(url_busqueda=slug)
        if exclude_id:
            query = query.filter(model_class.id != exclude_id)
        if not query.first():
            return slug
        slug = f'{base_slug}-{counter}'
        counter += 1
