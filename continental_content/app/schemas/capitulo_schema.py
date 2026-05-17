from .base_schema import BaseSchema
from app.schemas.arco_schema import ArcoSchema
from app.schemas.obra_schema import ObraSchema


class CapituloSchema(BaseSchema):

    @staticmethod
    def serialize(capitulo):
        data = BaseSchema.serialize_base(capitulo)
        data.update({
            'titulo': capitulo.titulo,
            'descripcion_larga': capitulo.descripcion_larga,
            'descripcion_corta': capitulo.descripcion_corta,
            'url_portada': capitulo.url_portada,
            'texto_capitulo': capitulo.texto_capitulo,
            'comentario_creador': capitulo.comentario_creador,
            'numero_capitulo': capitulo.numero_capitulo,
            'subarco_id': capitulo.subarco_id,
            'obra_id': capitulo.obra_id,
            'subarco': ArcoSchema.serialize(capitulo.subarco) if capitulo.subarco else None,
            'obra': ObraSchema.serialize(capitulo.obra) if capitulo.obra else None,
        })
        data.update(BaseSchema.serialize_seo(capitulo))
        return data

    @staticmethod
    def serialize_list(capitulos):
        return [CapituloSchema.serialize(c) for c in capitulos]

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('titulo'):
            errors.append('titulo es requerido')
        if data.get('numero_capitulo') is None:
            errors.append('numero_capitulo es requerido')
        if not data.get('obra_id'):
            errors.append('obra_id es requerido')
        return errors

    @staticmethod
    def validate_update(data):
        return []
