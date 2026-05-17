from .base_schema import BaseSchema
from app.schemas.personaje_ficticio_schema import PersonajeFicticioSchema


class NoticiaSchema(BaseSchema):

    @staticmethod
    def serialize(noticia):
        data = BaseSchema.serialize_base(noticia)
        data.update({
            'titulo': noticia.titulo,
            'descripcion_larga': noticia.descripcion_larga,
            'descripcion_corta': noticia.descripcion_corta,
            'url_portada': noticia.url_portada,
            'texto_noticia': noticia.texto_noticia,
            'autor_id': noticia.autor_id,
            'autor': PersonajeFicticioSchema.serialize(noticia.autor) if noticia.autor else None,
        })
        data.update(BaseSchema.serialize_seo(noticia))
        return data

    @staticmethod
    def serialize_list(noticias):
        return [NoticiaSchema.serialize(n) for n in noticias]

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('titulo'):
            errors.append('titulo es requerido')
        return errors

    @staticmethod
    def validate_update(data):
        return []
