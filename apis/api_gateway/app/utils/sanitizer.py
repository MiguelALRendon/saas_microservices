import re

_SCRIPT_RE = re.compile(
    r'<\s*script[^>]*>.*?<\s*/\s*script\s*>', re.IGNORECASE | re.DOTALL
)
_DANGEROUS_TAGS_RE = re.compile(
    r'<\s*(iframe|object|embed|form|input|button|meta|link|base)\b[^>]*>.*?<\s*/\s*\1\s*>',
    re.IGNORECASE | re.DOTALL,
)
_EVENT_HANDLERS_RE = re.compile(r'\bon\w+\s*=', re.IGNORECASE)

# Fields whose content must not be altered (passwords, rich text)
_SKIP_KEYS = {
    'contraseña', 'password',
    'texto_capitulo', 'texto_noticia', 'texto_nota', 'descripcion_larga',
}


def sanitize_string(value: str) -> str:
    """Strip dangerous HTML patterns from a plain string."""
    if not isinstance(value, str):
        return value
    value = _SCRIPT_RE.sub('', value)
    value = _DANGEROUS_TAGS_RE.sub('', value)
    value = _EVENT_HANDLERS_RE.sub('', value)
    value = value.replace('\x00', '')
    return value


def sanitize_dict(data: dict) -> dict:
    """Recursively sanitize all string values in a dict."""
    if not isinstance(data, dict):
        return data
    result = {}
    for key, value in data.items():
        if key in _SKIP_KEYS:
            result[key] = value
        elif isinstance(value, str):
            result[key] = sanitize_string(value)
        elif isinstance(value, dict):
            result[key] = sanitize_dict(value)
        elif isinstance(value, list):
            result[key] = _sanitize_list(value)
        else:
            result[key] = value
    return result


def sanitize_list(data: list) -> list:
    """Sanitize a top-level list of dicts or strings."""
    return _sanitize_list(data)


def _sanitize_list(lst: list) -> list:
    sanitized = []
    for item in lst:
        if isinstance(item, dict):
            sanitized.append(sanitize_dict(item))
        elif isinstance(item, str):
            sanitized.append(sanitize_string(item))
        else:
            sanitized.append(item)
    return sanitized
