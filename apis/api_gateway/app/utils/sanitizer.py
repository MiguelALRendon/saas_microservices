# Migrado a galurensoft_core.text (funciones puras) + skip-keys del borde de
# galurensoft_api_kit.sanitizer. Se conserva la API previa (sanitize_string/dict/list).
from galurensoft_core.text import sanitize_string
from galurensoft_core.text import sanitize_dict as _sanitize_dict
from galurensoft_core.text import sanitize_list as _sanitize_list
from galurensoft_api_kit.sanitizer import DEFAULT_SKIP_KEYS


def sanitize_dict(data: dict) -> dict:
    """Sanitiza recursivamente, omitiendo passwords y campos de texto enriquecido."""
    return _sanitize_dict(data, skip_keys=DEFAULT_SKIP_KEYS)


def sanitize_list(data: list) -> list:
    return _sanitize_list(data, skip_keys=DEFAULT_SKIP_KEYS)
