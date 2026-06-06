# Migrado a galurensoft_core.crud (build_blueprint).
# NOTA (bug fix): el código original validaba fkSistema como requerido pero NUNCA lo
# persistía en create/update (y la columna es NOT NULL), por lo que crear una empresa
# siempre fallaba con 500. Aquí fkSistema se incluye en create_fields/editable para que
# la creación funcione, alineando el comportamiento con la validación existente.
from app import db
from app.models.empresa import Empresa
from app.schemas.empresa_schema import EmpresaSchema
from galurensoft_core.crud import ResourceDescriptor, build_blueprint

empresa_bp = build_blueprint(ResourceDescriptor(
    model=Empresa,
    name='empresa',
    url_prefix='/empresa',
    session=lambda: db.session,
    serialize=EmpresaSchema.serialize,
    serialize_list=EmpresaSchema.serialize_list,
    serialize_detail=EmpresaSchema.serialize_detail,
    create_fields=['clave', 'nombre', 'folio', 'urlLogo', 'direccion', 'telefono', 'email', 'fkSistema'],
    editable=['clave', 'nombre', 'folio', 'urlLogo', 'direccion', 'telefono', 'email', 'fkSistema'],
    filters={'clave': 'ilike', 'nombre': 'ilike', 'email': 'ilike'},
    unique={'clave': 'La clave ya existe'},
    conflict_status=400,
    validate_create=EmpresaSchema.validate_create,
    validate_update=EmpresaSchema.validate_update,
    not_found_message='Empresa no encontrada',
    delete_message='Empresa eliminada exitosamente',
    not_a_list_message='Se esperaba una lista de empresas',
    include_has_more=False,
))
