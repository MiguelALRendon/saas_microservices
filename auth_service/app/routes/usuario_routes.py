# Migrado a galurensoft_core.crud. La contraseña se hashea con hooks before_create/before_update
# (nunca se serializa). Validación -> 422, conflicto -> 400 (contrato del auth_service).
from app import db
from app.models.usuario import Usuario
from app.schemas.usuario_schema import UsuarioSchema
from app.utils import hash_password
from galurensoft_core.crud import Hooks, ResourceDescriptor, build_blueprint


def _hash_create(data):
    return {**data, 'contraseña': hash_password(data['contraseña'])}


def _hash_update(obj, data):
    # Sólo re-hashea si viene una contraseña no vacía; si no, no la toca.
    if data.get('contraseña'):
        return {**data, 'contraseña': hash_password(data['contraseña'])}
    cleaned = dict(data)
    cleaned.pop('contraseña', None)
    return cleaned


usuario_bp = build_blueprint(ResourceDescriptor(
    model=Usuario,
    name='usuario',
    url_prefix='/usuario',
    session=lambda: db.session,
    serialize=UsuarioSchema.serialize,
    serialize_list=UsuarioSchema.serialize_list,
    serialize_detail=UsuarioSchema.serialize_detail,
    create_fields=['usuario', 'contraseña', 'fkSistema'],
    editable=['usuario', 'contraseña', 'fkSistema'],
    filters={'usuario': 'ilike', 'fkSistema': 'eq'},
    unique={'usuario': 'El usuario ya existe'},
    conflict_status=400,
    validation_status=422,
    validate_create=UsuarioSchema.validate_create,
    validate_update=UsuarioSchema.validate_update,
    hooks=Hooks(before_create=_hash_create, before_update=_hash_update),
    not_found_message='Usuario no encontrado',
    delete_message='Usuario eliminado exitosamente',
    not_a_list_message='Se esperaba una lista de usuarios',
    include_has_more=False,
))
