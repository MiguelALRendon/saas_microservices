# Migrado a galurensoft_core: columnas base via mixin PosBase.
from app import db
from galurensoft_core.persistence import PosBase


class BaseObject(db.Model, PosBase):
    __abstract__ = True
