# Migrado a galurensoft_core.password (Argon2). Se conservan las funciones previas.
from galurensoft_core.password import hash_password, needs_rehash, verify_password

__all__ = ['hash_password', 'verify_password', 'needs_rehash']
