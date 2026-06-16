# Migrado a galurensoft_core.crud. FIX: persiste fkEmpresa (el original lo validaba pero no
# lo guardaba; columna NOT NULL -> create 500).
from app import db
from app.enums import BaseObjectEstatus
from app.models.cargo import Cargo
from app.schemas.cargo_schema import CargoSchema
from galurensoft_core.crud import ResourceDescriptor, build_blueprint
from galurensoft_core.persistence import StatusPolicy

_status = StatusPolicy.enum(enum_cls=BaseObjectEstatus)

cargo_bp = build_blueprint(ResourceDescriptor(
    model=Cargo,
    name='cargo',
    url_prefix='/cargo',
    session=lambda: db.session,
    status=_status,
    serialize=CargoSchema.serialize,
    serialize_list=CargoSchema.serialize_list,
    serialize_detail=CargoSchema.serialize_detail,
    create_fields=['clave', 'nombre', 'fkEmpresa'],
    editable=['clave', 'nombre'],
    filters={'clave': 'ilike', 'nombre': 'ilike', 'fkEmpresa': 'eq'},
    unique={'clave': 'La clave ya existe'},
    conflict_status=400,
    validation_status=400,
    validate_create=CargoSchema.validate_create,
    validate_update=CargoSchema.validate_update,
    not_found_message='Cargo no encontrado',
    delete_message='Cargo eliminado exitosamente',
    not_a_list_message='Se esperaba una lista de cargos',
    include_has_more=False,
))
