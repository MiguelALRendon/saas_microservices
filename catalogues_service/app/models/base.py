# Migrado a galurensoft_core: las columnas base (oid, createdAt, updatedAt, creado_por,
# editado_por, estatus) las aporta el mixin PosBase de la librería compartida. La clase
# concreta sigue llamándose BaseObject para no romper los modelos existentes.
from app import db
from galurensoft_core.persistence import PosBase


class BaseObject(db.Model, PosBase):
    __abstract__ = True
