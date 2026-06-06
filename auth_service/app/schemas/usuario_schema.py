from .base_schema import BaseSchema
from app.enums import BaseObjectEstatus


class UsuarioSchema(BaseSchema):
    """Schema para serialización y validación de Usuario."""

    @staticmethod
    def serialize(usuario, _cache=None):
        """Plana — usa cache para sistema externo."""
        from app.external_catalogues.sistema_external import SistemaExternal

        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        data = BaseSchema.serialize_base(usuario)
        data.update({
            'usuario': usuario.usuario,
            'fkSistema': usuario.fkSistema,
            'sistema': BaseSchema.resolve_external(cache, 'sistema', usuario.fkSistema, SistemaExternal),
        })
        # contraseña nunca se incluye
        return data

    @staticmethod
    def serialize_list(usuarios, _cache=None):
        """Pre-batch de sistemas → 1 HTTP total sin importar N."""
        from app.external_catalogues.sistema_external import SistemaExternal

        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        BaseSchema.prefetch_external(cache, 'sistema', [u.fkSistema for u in usuarios], SistemaExternal)
        return [UsuarioSchema.serialize(u, _cache=cache) for u in usuarios]

    @staticmethod
    def serialize_detail(usuario, per_page: int = 25, _cache=None):
        """Detalle paginado: roles (interno), empleados (junction local + external), sucursales (junction local + external)."""
        from .rol_schema import RolSchema
        from .permiso_asignado_schema import PermisoAsignadoSchema
        from app.models.usuario_rol import UsuarioRol
        from app.models.usuario_empleado import UsuarioEmpleado
        from app.models.usuario_sucursal import UsuarioSucursal
        from app.models.permiso_asignado import PermisoAsignado
        from app.external_branch.empleado_external import EmpleadoExternal
        from app.external_catalogues.sucursal_external import SucursalExternal

        cache = _cache if _cache is not None else BaseSchema.empty_cache()
        data = UsuarioSchema.serialize(usuario, _cache=cache)

        # ── Roles vía usuario_rol (junction interna) — detalle completo con permisos
        roles_q = usuario.usuario_roles.filter(UsuarioRol.estatus == BaseObjectEstatus.ACTIVO)

        def _serialize_roles(usuario_roles):
            roles = [ur.rol for ur in usuario_roles if ur.rol and ur.rol.estatus == BaseObjectEstatus.ACTIVO]
            # Pre-fetch de permisos_asignados de todos los roles de esta página, en una sola query
            rol_oids = [r.oid for r in roles]
            permisos_por_rol = {oid: [] for oid in rol_oids}
            if rol_oids:
                pa_list = PermisoAsignado.query.filter(
                    PermisoAsignado.fkRol.in_(rol_oids),
                    PermisoAsignado.estatus == BaseObjectEstatus.ACTIVO,
                ).all()
                for pa in pa_list:
                    permisos_por_rol.setdefault(pa.fkRol, []).append(pa)
            out = []
            for rol in roles:
                rol_data = RolSchema.serialize(rol, _cache=cache)
                rol_data['permisos_asignados'] = [
                    PermisoAsignadoSchema.serialize_compact(pa, omit='rol', _cache=cache)
                    for pa in permisos_por_rol.get(rol.oid, [])
                ]
                out.append(rol_data)
            return out

        data['roles'] = BaseSchema.paginate_local(roles_q, _serialize_roles, per_page=per_page)

        # ── Empleados vía usuario_empleado (junction local + external batch)
        empleados_junction_q = usuario.usuario_empleados.filter(
            UsuarioEmpleado.estatus == BaseObjectEstatus.ACTIVO
        )
        data['empleados'] = BaseSchema.paginate_junction_external(
            cache=cache,
            junction_query=empleados_junction_q,
            fk_attr='fkEmpleado',
            cache_key='empleado',
            external_class=EmpleadoExternal,
            per_page=per_page,
        )

        # ── Sucursales vía usuario_sucursal (junction local + external batch)
        sucursales_junction_q = usuario.usuario_sucursales.filter(
            UsuarioSucursal.estatus == BaseObjectEstatus.ACTIVO
        )
        data['sucursales'] = BaseSchema.paginate_junction_external(
            cache=cache,
            junction_query=sucursales_junction_q,
            fk_attr='fkSucursal',
            cache_key='sucursal',
            external_class=SucursalExternal,
            per_page=per_page,
        )

        return data

    @staticmethod
    def validate_create(data):
        errors = []
        if not data.get('usuario'):
            errors.append('usuario es requerido')
        if not data.get('contraseña'):
            errors.append('contraseña es requerida')
        if not data.get('fkSistema'):
            errors.append('fkSistema es requerido')
        return errors

    @staticmethod
    def validate_update(data):
        return []
