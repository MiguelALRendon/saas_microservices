# Migrado a galurensoft_core.web.create_service_app.
# NOTA: base.py/base_contacto.py/enums/base_schema se mantienen LOCALES porque branch usa
# un BaseObjectEstatus con un valor extra (CANCELADO) — no se puede compartir el enum del core.
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from galurensoft_core.web import create_service_app

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    from app.routes import (
        cargo_bp,
        empleado_bp,
        turno_sucursal_bp,
        corte_caja_bp,
        empleado_sucursal_bp,
        turno_empleado_bp,
    )

    def on_models():
        from app import models  # noqa: F401

    return create_service_app(
        config=Config,
        db=db,
        migrate=migrate,
        migrate_table='alembic_version_branch',
        blueprints=[
            cargo_bp, empleado_bp, turno_sucursal_bp,
            corte_caja_bp, empleado_sucursal_bp, turno_empleado_bp,
        ],
        on_models=on_models,
    )
