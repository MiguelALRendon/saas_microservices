from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Configurar el hasher de Argon2
ph = PasswordHasher()

def hash_password(password):
    """
    Hashea una contraseña usando Argon2.
    
    Args:
        password (str): Contraseña en texto plano
        
    Returns:
        str: Contraseña hasheada
    """
    return ph.hash(password)

def verify_password(hashed_password, password):
    """
    Verifica si una contraseña coincide con su hash.
    
    Args:
        hashed_password (str): Contraseña hasheada
        password (str): Contraseña en texto plano a verificar
        
    Returns:
        bool: True si la contraseña coincide, False en caso contrario
    """
    try:
        ph.verify(hashed_password, password)
        return True
    except VerifyMismatchError:
        return False

def needs_rehash(hashed_password):
    """
    Verifica si una contraseña necesita ser re-hasheada.
    Útil cuando se actualizan los parámetros de Argon2.
    
    Args:
        hashed_password (str): Contraseña hasheada
        
    Returns:
        bool: True si necesita re-hash, False en caso contrario
    """
    return ph.check_needs_rehash(hashed_password)
