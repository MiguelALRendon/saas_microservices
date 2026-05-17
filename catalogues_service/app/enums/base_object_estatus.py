from enum import Enum

class BaseObjectEstatus(str, Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    ELIMINADO = "ELIMINADO"
