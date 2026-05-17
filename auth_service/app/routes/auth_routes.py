from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from app.models.usuario import Usuario
from app.models.usuario_rol import UsuarioRol
from app.models.permiso_asignado import PermisoAsignado
from app.utils import verify_password
from app.enums import BaseObjectEstatus
from datetime import timedelta

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def _build_roles_payload(usuario):
    roles_data = []
    active_usuario_roles = usuario.usuario_roles.filter(
        UsuarioRol.estatus == BaseObjectEstatus.ACTIVO
    ).all()

    for ur in active_usuario_roles:
        rol = ur.rol
        if not rol or rol.estatus != BaseObjectEstatus.ACTIVO:
            continue

        permisos_asignados = PermisoAsignado.query.filter(
            PermisoAsignado.fkRol == rol.oid,
            PermisoAsignado.estatus == BaseObjectEstatus.ACTIVO,
        ).all()

        permisos_data = []
        for pa in permisos_asignados:
            permiso = pa.permiso
            if not permiso or permiso.estatus != BaseObjectEstatus.ACTIVO:
                continue
            permisos_data.append({
                'clave': permiso.clave,
                'nombre': permiso.nombre,
                'permiso': permiso.permiso,
                'crear': pa.crear,
                'editar': pa.editar,
                'desactivar': pa.desactivar,
                'cancelar': pa.cancelar,
            })

        roles_data.append({
            'oid': rol.oid,
            'nombre': rol.nombre,
            'permisos': permisos_data,
        })

    return roles_data


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'errors': ['No se proporcionaron datos']}), 400

        usuario_str = data.get('usuario')
        password = data.get('contraseña')

        if not usuario_str:
            return jsonify({'errors': ['usuario es requerido']}), 400

        if not password:
            return jsonify({'errors': ['contraseña es requerida']}), 400

        usuario = Usuario.query.filter(
            Usuario.usuario == usuario_str,
            Usuario.estatus == BaseObjectEstatus.ACTIVO
        ).first()

        if not usuario:
            return jsonify({'errors': ['Credenciales inválidas']}), 401

        if not verify_password(usuario.contraseña, password):
            return jsonify({'errors': ['Credenciales inválidas']}), 401

        access_token = create_access_token(
            identity=usuario.oid,
            expires_delta=timedelta(hours=1)
        )
        refresh_token = create_refresh_token(
            identity=usuario.oid,
            expires_delta=timedelta(days=30)
        )

        from app.schemas.usuario_schema import UsuarioSchema

        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'usuario': UsuarioSchema.serialize(usuario),
            'roles': _build_roles_payload(usuario),
        }), 200

    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        identity = get_jwt_identity()
        new_access_token = create_access_token(
            identity=identity,
            expires_delta=timedelta(hours=1)
        )
        return jsonify({'access_token': new_access_token}), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
