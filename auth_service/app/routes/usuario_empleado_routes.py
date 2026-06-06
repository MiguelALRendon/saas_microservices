from flask import Blueprint, request, jsonify
from app import db
from app.models.usuario_empleado import UsuarioEmpleado
from app.models.usuario import Usuario
from app.schemas.usuario_empleado_schema import UsuarioEmpleadoSchema
from app.enums import BaseObjectEstatus
from datetime import datetime

usuario_empleado_bp = Blueprint('usuario_empleado', __name__, url_prefix='/usuario-empleado')


@usuario_empleado_bp.route('/<string:oid>', methods=['GET'])
def get_usuario_empleado(oid):
    try:
        item = UsuarioEmpleado.query.filter(
            UsuarioEmpleado.oid == oid,
            UsuarioEmpleado.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        if not item:
            return jsonify({'errors': ['Asignación no encontrada']}), 404
        return jsonify(UsuarioEmpleadoSchema.serialize(item)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@usuario_empleado_bp.route('/', methods=['GET'])
def get_usuario_empleados():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        fk_usuario = request.args.get('fkUsuario', type=str)
        fk_empleado = request.args.get('fkEmpleado', type=str)

        query = UsuarioEmpleado.query.filter(UsuarioEmpleado.estatus != BaseObjectEstatus.ELIMINADO)
        if fk_usuario:
            query = query.filter(UsuarioEmpleado.fkUsuario == fk_usuario)
        if fk_empleado:
            query = query.filter(UsuarioEmpleado.fkEmpleado == fk_empleado)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'data': UsuarioEmpleadoSchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@usuario_empleado_bp.route('/', methods=['POST'])
def create_usuario_empleado():
    try:
        data = request.get_json() or {}
        errors = UsuarioEmpleadoSchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 400

        usuario = Usuario.query.filter(
            Usuario.oid == data['fkUsuario'],
            Usuario.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        if not usuario:
            return jsonify({'errors': ['El usuario no existe']}), 400

        existing = UsuarioEmpleado.query.filter(
            UsuarioEmpleado.fkUsuario == data['fkUsuario'],
            UsuarioEmpleado.fkEmpleado == data['fkEmpleado'],
            UsuarioEmpleado.estatus != BaseObjectEstatus.ELIMINADO,
        ).first()
        if existing:
            return jsonify({'errors': ['La asignación ya existe']}), 400

        item = UsuarioEmpleado(
            fkUsuario=data['fkUsuario'],
            fkEmpleado=data['fkEmpleado'],
            creado_por=data.get('creado_por'),
            estatus=BaseObjectEstatus.ACTIVO,
        )
        db.session.add(item)
        db.session.commit()
        return jsonify(UsuarioEmpleadoSchema.serialize(item)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@usuario_empleado_bp.route('/many', methods=['POST'])
def create_many_usuario_empleados():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de asignaciones']}), 400

        created = []
        errors = []
        for idx, item in enumerate(data):
            validation_errors = UsuarioEmpleadoSchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            existing = UsuarioEmpleado.query.filter(
                UsuarioEmpleado.fkUsuario == item['fkUsuario'],
                UsuarioEmpleado.fkEmpleado == item['fkEmpleado'],
                UsuarioEmpleado.estatus != BaseObjectEstatus.ELIMINADO,
            ).first()
            if existing:
                errors.append({'index': idx, 'errors': ['La asignación ya existe']})
                continue
            entity = UsuarioEmpleado(
                fkUsuario=item['fkUsuario'],
                fkEmpleado=item['fkEmpleado'],
                creado_por=item.get('creado_por'),
                estatus=BaseObjectEstatus.ACTIVO,
            )
            db.session.add(entity)
            created.append(entity)

        if created:
            db.session.commit()

        response = {'created': len(created), 'data': UsuarioEmpleadoSchema.serialize_list(created)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@usuario_empleado_bp.route('/<string:oid>', methods=['PUT'])
def update_usuario_empleado(oid):
    try:
        item = UsuarioEmpleado.query.filter(
            UsuarioEmpleado.oid == oid,
            UsuarioEmpleado.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        if not item:
            return jsonify({'errors': ['Asignación no encontrada']}), 404

        data = request.get_json() or {}
        if 'editado_por' in data:
            item.editado_por = data['editado_por']
        item.updatedAt = datetime.utcnow()
        db.session.commit()
        return jsonify(UsuarioEmpleadoSchema.serialize(item)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@usuario_empleado_bp.route('/many', methods=['PUT'])
def update_many_usuario_empleados():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de asignaciones']}), 400

        updated = []
        errors = []
        for idx, item in enumerate(data):
            if 'oid' not in item:
                errors.append({'index': idx, 'errors': ['oid es requerido']})
                continue
            entity = UsuarioEmpleado.query.filter(
                UsuarioEmpleado.oid == item['oid'],
                UsuarioEmpleado.estatus != BaseObjectEstatus.ELIMINADO
            ).first()
            if not entity:
                errors.append({'index': idx, 'errors': ['Asignación no encontrada']})
                continue
            if 'editado_por' in item:
                entity.editado_por = item['editado_por']
            entity.updatedAt = datetime.utcnow()
            updated.append(entity)

        if updated:
            db.session.commit()

        response = {'updated': len(updated), 'data': UsuarioEmpleadoSchema.serialize_list(updated)}
        if errors:
            response['errors'] = errors
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@usuario_empleado_bp.route('/<string:oid>', methods=['DELETE'])
def delete_usuario_empleado(oid):
    try:
        item = UsuarioEmpleado.query.filter(
            UsuarioEmpleado.oid == oid,
            UsuarioEmpleado.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        if not item:
            return jsonify({'errors': ['Asignación no encontrada']}), 404

        data = request.get_json() or {}
        item.estatus = BaseObjectEstatus.ELIMINADO
        item.editado_por = data.get('editado_por')
        item.updatedAt = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Asignación eliminada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500


@usuario_empleado_bp.route('/list', methods=['POST'])
def get_usuario_empleado_list():
    try:
        data = request.get_json()
        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400
        oid_list = data.get('oid_list', [])
        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400
        items = UsuarioEmpleado.query.filter(
            UsuarioEmpleado.oid.in_(oid_list),
            UsuarioEmpleado.estatus != BaseObjectEstatus.ELIMINADO
        ).all()
        return jsonify(UsuarioEmpleadoSchema.serialize_list(items)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
