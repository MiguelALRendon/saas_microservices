# Migrado a galurensoft_core: este enum ahora vive en la librería compartida.
# Se re-exporta para no romper los imports existentes (`from app.enums import BaseObjectEstatus`).
from galurensoft_core.persistence import BaseObjectEstatus

__all__ = ['BaseObjectEstatus']
