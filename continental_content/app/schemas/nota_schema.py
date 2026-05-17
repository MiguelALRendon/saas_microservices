from .base_schema import BaseSchema
from app.schemas.obra_schema import ObraSchema
from app.schemas.arco_schema import ArcoSchema


class NotaSchema(BaseSchema):

    @staticmethod
    def serialize(nota):
        data = BaseSchema.serialize_concept_base(nota)
        data.update({
            'titulo_nota': nota.titulo_nota,
            'texto_nota': nota.texto_nota,
            'fk_obra': nota.fk_obra,
            'fk_arco': nota.fk_arco,
            'obra': ObraSchema.serialize(nota.obra) if nota.obra else None,
            'arco': ArcoSchema.serialize(nota.arco) if nota.arco else None,
        })
        return data

    @staticmethod
    def serialize_list(notas):
        return [NotaSchema.serialize(n) for n in notas]

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('titulo_nota'):
            errors.append('titulo_nota es requerido')
        if not data.get('texto_nota'):
            errors.append('texto_nota es requerido')
        if not data.get('fk_obra'):
            errors.append('fk_obra es requerido')
        return errors

    @staticmethod
    def validate_update(data):
        return []
