# Migrado a galurensoft_core.crud. Junction Usuario↔Rol.
# Validación -> 422; conflicto -> 400; unicidad compuesta (fkUsuario, fkRol) considerando
# TODOS los registros (incl. eliminados) como el original (filter_by).
from app import db
from app.models.usuario_rol import UsuarioRol
from app.schemas.usuario_rol_schema import UsuarioRolSchema
from galurensoft_core.crud import ResourceDescriptor, build_blueprint

usuario_rol_bp = build_blueprint(ResourceDescriptor(
    model=UsuarioRol,
    name='usuario_rol',
    url_prefix='/usuario_rol',
    session=lambda: db.session,
    serialize=UsuarioRolSchema.serialize,
    serialize_list=UsuarioRolSchema.serialize_list,
    create_fields=['fkUsuario', 'fkRol'],
    editable=[],
    filters={'fkUsuario': 'eq', 'fkRol': 'eq'},
    unique_together=[(('fkUsuario', 'fkRol'), 'El rol ya está asignado a este usuario')],
    conflict_status=400,
    validation_status=422,
    validate_create=UsuarioRolSchema.validate_create,
    validate_update=UsuarioRolSchema.validate_update,
    not_found_message='Usuario-Rol no encontrado',
    delete_message='Usuario-Rol eliminado exitosamente',
    not_a_list_message='Se esperaba una lista de usuario_roles',
    include_has_more=False,
))
