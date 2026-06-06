# Migrado a galurensoft_core: PosContactoBase = PosBase + telefono + email.
from app import db
from galurensoft_core.persistence import PosContactoBase


class BaseContactoObject(db.Model, PosContactoBase):
    __abstract__ = True
