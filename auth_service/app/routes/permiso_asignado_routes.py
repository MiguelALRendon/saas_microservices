# Migrado a galurensoft_core.crud. Junction Rol↔Permiso con atributos booleanos.
# Unicidad compuesta (fkRol, fkPermiso). editable: solo los booleanos (no los FK).
from app import db
from app.models.permiso_asignado import PermisoAsignado
from app.schemas.permiso_asignado_schema import PermisoAsignadoSchema
from galurensoft_core.crud import ResourceDescriptor, build_blueprint

permiso_asignado_bp = build_blueprint(ResourceDescriptor(
    model=PermisoAsignado,
    name='permiso_asignado',
    url_prefix='/permiso_asignado',
    session=lambda: db.session,
    serialize=PermisoAsignadoSchema.serialize,
    serialize_list=PermisoAsignadoSchema.serialize_list,
    create_fields=['fkPermiso', 'fkRol', 'crear', 'editar', 'desactivar', 'cancelar'],
    editable=['crear', 'editar', 'desactivar', 'cancelar'],
    filters={'fkRol': 'eq', 'fkPermiso': 'eq'},
    unique_together=[(('fkRol', 'fkPermiso'), 'El permiso ya está asignado a este rol')],
    conflict_status=400,
    validation_status=422,
    validate_create=PermisoAsignadoSchema.validate_create,
    validate_update=PermisoAsignadoSchema.validate_update,
    not_found_message='Permiso asignado no encontrado',
    delete_message='Permiso asignado eliminado exitosamente',
    not_a_list_message='Se esperaba una lista de permisos asignados',
    include_has_more=False,
))
