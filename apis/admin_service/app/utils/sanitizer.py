# Sanitización de borde (galurensoft_core.text + skip-keys de galurensoft_api_kit).
from galurensoft_core.text import sanitize_string
from galurensoft_core.text import sanitize_dict as _sanitize_dict
from galurensoft_core.text import sanitize_list as _sanitize_list
from galurensoft_api_kit.sanitizer import DEFAULT_SKIP_KEYS


def sanitize_dict(data: dict) -> dict:
    return _sanitize_dict(data, skip_keys=DEFAULT_SKIP_KEYS)


def sanitize_list(data: list) -> list:
    return _sanitize_list(data, skip_keys=DEFAULT_SKIP_KEYS)
