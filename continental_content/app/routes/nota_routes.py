# Migrado a galurensoft_core.crud. Nota es ConceptBase (sin estatus): borrado FÍSICO.
from app import db
from app.models.nota import Nota
from app.models.obra import Obra
from app.schemas.nota_schema import NotaSchema
from app.routes._helpers import hard_delete_extra
from galurensoft_core.crud import ResourceDescriptor, build_blueprint
from galurensoft_core.persistence import CONTINENTAL

_ENDPOINTS = ('get_one', 'get_list', 'create', 'create_many', 'update', 'update_many', 'list')


def _validate_create(data):
    errors = NotaSchema.validate_create(data)
    if not errors:
        obra = Obra.query.filter(Obra.id == data['fk_obra'], Obra.estatus == 1).first()
        if not obra:
            errors.append('La obra especificada no existe')
    return errors


nota_bp = build_blueprint(
    ResourceDescriptor(
        model=Nota,
        name='nota',
        url_prefix='/nota',
        session=lambda: db.session,
        naming=CONTINENTAL,
        status=None,  # ConceptBase: sin estatus
        serialize=NotaSchema.serialize,
        serialize_list=NotaSchema.serialize_list,
        create_fields=['titulo_nota', 'texto_nota', 'fk_obra', 'fk_arco'],
        editable=['titulo_nota', 'texto_nota', 'fk_obra', 'fk_arco'],
        filters={'fk_obra': 'eq', 'fk_arco': 'eq'},
        validation_status=400,
        validate_create=_validate_create,
        validate_update=NotaSchema.validate_update,
        not_found_message='Nota no encontrada',
        not_a_list_message='Se esperaba una lista de notas',
        include_has_more=False,
    ),
    endpoints=_ENDPOINTS,
    extra=hard_delete_extra(Nota, not_found='Nota no encontrada', message='Nota eliminada exitosamente'),
)
