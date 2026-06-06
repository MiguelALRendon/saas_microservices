# Migrado a galurensoft_core.crud (build_blueprint).
# - filtro is_especial via modo "bool"
# - unidadMedida (Enum) se coacciona de string a UnidadMedida con hooks before_create/before_update
# - doble unicidad: clave + codigo_barras
from app import db
from app.models.producto import Producto
from app.schemas.producto_schema import ProductoSchema
from app.enums import UnidadMedida
from galurensoft_core.crud import Hooks, ResourceDescriptor, build_blueprint


def _coerce_unidad(data):
    """Convierte unidadMedida de string a UnidadMedida (no muta el payload original)."""
    if isinstance(data.get('unidadMedida'), str):
        return {**data, 'unidadMedida': UnidadMedida[data['unidadMedida'].upper()]}
    return data


producto_bp = build_blueprint(ResourceDescriptor(
    model=Producto,
    name='producto',
    url_prefix='/producto',
    session=lambda: db.session,
    serialize=ProductoSchema.serialize,
    serialize_list=ProductoSchema.serialize_list,
    create_fields=['clave', 'nombre', 'codigo_barras', 'unidadMedida', 'is_especial', 'fkProveedorMarca'],
    editable=['clave', 'nombre', 'codigo_barras', 'unidadMedida', 'is_especial', 'fkProveedorMarca'],
    filters={'clave': 'ilike', 'nombre': 'ilike', 'codigo_barras': 'ilike', 'is_especial': 'bool'},
    unique={'clave': 'La clave ya existe', 'codigo_barras': 'El código de barras ya existe'},
    validate_create=ProductoSchema.validate_create,
    validate_update=ProductoSchema.validate_update,
    hooks=Hooks(
        before_create=_coerce_unidad,
        before_update=lambda obj, data: _coerce_unidad(data),
    ),
    not_found_message='Producto no encontrado',
    delete_message='Producto eliminado exitosamente',
    not_a_list_message='Se esperaba una lista de productos',
    include_has_more=False,
))
