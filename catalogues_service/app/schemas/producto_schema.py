# Migrado a galurensoft_core: serialize_audit + campos propios (unidadMedida se serializa
# por su .value). La validación de unidadMedida se conserva igual.
from galurensoft_core.serialization import serialize_audit
from app.enums import UnidadMedida


class ProductoSchema:
    """Schema para serialización y validación de Producto."""

    @staticmethod
    def serialize(producto, _cache=None):
        data = serialize_audit(producto)
        data.update({
            'clave': producto.clave,
            'nombre': producto.nombre,
            'codigo_barras': producto.codigo_barras,
            'unidadMedida': producto.unidadMedida.value if producto.unidadMedida else None,
            'is_especial': producto.is_especial,
            'fkProveedorMarca': producto.fkProveedorMarca,
        })
        return data

    @staticmethod
    def serialize_list(productos, _cache=None):
        return [ProductoSchema.serialize(p, _cache=_cache) for p in productos]

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('clave'):
            errors.append('clave es requerida')
        if not data.get('nombre'):
            errors.append('nombre es requerido')
        if not data.get('unidadMedida'):
            errors.append('unidadMedida es requerida')
        else:
            try:
                if isinstance(data['unidadMedida'], str):
                    UnidadMedida[data['unidadMedida'].upper()]
            except KeyError:
                errors.append(f"unidadMedida inválida: {data['unidadMedida']}")
        if not data.get('fkProveedorMarca'):
            errors.append('fkProveedorMarca es requerido')
        return errors

    @staticmethod
    def validate_update(data):
        errors = []
        if 'unidadMedida' in data and data['unidadMedida']:
            try:
                if isinstance(data['unidadMedida'], str):
                    UnidadMedida[data['unidadMedida'].upper()]
            except KeyError:
                errors.append(f"unidadMedida inválida: {data['unidadMedida']}")
        return errors
