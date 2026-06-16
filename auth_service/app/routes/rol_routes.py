# Migrado a galurensoft_core.crud. rol NO expone /many.
# FIX: el original validaba fkSistema pero no lo persistía (NOT NULL) -> create 500;
# aquí fkSistema/fkEmpresa se incluyen en create_fields.
from app import db
from app.models.rol import Rol
from app.schemas.rol_schema import RolSchema
from galurensoft_core.crud import ResourceDescriptor, build_blueprint

rol_bp = build_blueprint(
    ResourceDescriptor(
        model=Rol,
        name='rol',
        url_prefix='/rol',
        session=lambda: db.session,
        serialize=RolSchema.serialize,
        serialize_list=RolSchema.serialize_list,
        serialize_detail=RolSchema.serialize_detail,
        create_fields=['nombre', 'fkSistema', 'fkEmpresa'],
        editable=['nombre'],
        filters={'nombre': 'ilike'},
        unique={'nombre': 'El nombre de rol ya existe'},
        conflict_status=400,
        validation_status=422,
        validate_create=RolSchema.validate_create,
        validate_update=RolSchema.validate_update,
        not_found_message='Rol no encontrado',
        delete_message='Rol eliminado exitosamente',
        include_has_more=False,
    ),
    endpoints=('get_one', 'get_list', 'create', 'update', 'delete', 'list'),  # sin /many
)
