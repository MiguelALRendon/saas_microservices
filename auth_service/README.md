# Auth Service

Microservicio de autenticación y gestión de usuarios del sistema SaaS.

## 📋 Descripción

El servicio de autenticación maneja todo lo relacionado con usuarios, roles, permisos y sus asignaciones. Proporciona un sistema completo de control de acceso basado en roles (RBAC).

## 🗄️ Modelos incluidos

- **Usuario**: Gestión de usuarios con información personal y relaciones con Empresa, Sucursal y Sistema
- **Rol**: Definición de roles del sistema
- **Permiso**: Catálogo de permisos disponibles
- **PermisoAsignado**: Asignación de permisos a roles con permisos CRUD específicos
- **UsuarioRol**: Relación muchos a muchos entre usuarios y roles

## 🚀 Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Copiar `.env.example` a `.env` y configurar:

```bash
cp .env.example .env
```

Editar `.env` con tus valores:

```bash
# Application Settings
SECRET_KEY=tu-clave-secreta
JWT_SECRET_KEY=tu-clave-jwt-secreta

# Database Configuration
DATABASE_URL=mysql+pymysql://usuario:password@localhost:3306/microservices_db

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False
BASE_URL=http://localhost:8000
```

### 3. Iniciar el servidor

```bash
python run.py
```

El servidor se iniciará en `http://localhost:8000`

## 📡 Endpoints

Cada entidad tiene 7 endpoints estándar:

### Usuario (`/usuario`)

- `GET /usuario/<oid>` - Obtener usuario por OID
- `GET /usuario/` - Listar usuarios (paginación y filtros)
- `POST /usuario/` - Crear usuario
- `PUT /usuario/<oid>` - Actualizar usuario
- `DELETE /usuario/<oid>` - Eliminar usuario (soft delete)

**Nota:** No se permiten operaciones múltiples para usuarios (`/many` no disponible)

**Filtros disponibles:** `usuario`, `fkEmpleado`

### Rol (`/rol`)

- `GET /rol/<oid>` - Obtener rol por OID
- `GET /rol/` - Listar roles (paginación y filtros)
- `POST /rol/` - Crear rol
- `PUT /rol/<oid>` - Actualizar rol
- `DELETE /rol/<oid>` - Eliminar rol (soft delete)

**Nota:** No se permiten operaciones múltiples para roles (`/many` no disponible)

**Filtros disponibles:** `nombre`

### Permiso (`/permiso`)

- `GET /permiso/<oid>` - Obtener permiso por OID
- `GET /permiso/` - Listar permisos (paginación y filtros)
- `POST /permiso/` - Crear permiso
- `POST /permiso/many` - Crear múltiples permisos
- `PUT /permiso/<oid>` - Actualizar permiso
- `PUT /permiso/many` - Actualizar múltiples permisos
- `DELETE /permiso/<oid>` - Eliminar permiso (soft delete)

**Filtros disponibles:** `clave`, `nombre`, `permiso`

### PermisoAsignado (`/permiso_asignado`)

- `GET /permiso_asignado/<oid>` - Obtener permiso asignado por OID
- `GET /permiso_asignado/` - Listar permisos asignados (paginación y filtros)
- `POST /permiso_asignado/` - Crear permiso asignado
- `POST /permiso_asignado/many` - Crear múltiples permisos asignados
- `PUT /permiso_asignado/<oid>` - Actualizar permiso asignado
- `PUT /permiso_asignado/many` - Actualizar múltiples permisos asignados
- `DELETE /permiso_asignado/<oid>` - Eliminar permiso asignado (soft delete)

**Filtros disponibles:** `fkRol`, `fkPermiso`

### UsuarioRol (`/usuario_rol`)

- `GET /usuario_rol/<oid>` - Obtener usuario-rol por OID
- `GET /usuario_rol/` - Listar usuario-roles (paginación y filtros)
- `POST /usuario_rol/` - Crear usuario-rol
- `POST /usuario_rol/many` - Crear múltiples usuario-roles
- `PUT /usuario_rol/<oid>` - Actualizar usuario-rol
- `PUT /usuario_rol/many` - Actualizar múltiples usuario-roles
- `DELETE /usuario_rol/<oid>` - Eliminar usuario-rol (soft delete)

**Filtros disponibles:** `fkUsuario`, `fkRol`

## 📝 Ejemplos de uso

### Crear un usuario

```bash
curl -X POST http://localhost:8000/usuario/ \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": "jperez",
    "contraseña": "password123",
    "fkSistema": "uuid-sistema",
    "fkEmpleado": "uuid-empleado",
    "creado_por": "uuid-admin"
  }'
```

### Listar usuarios con paginación y filtros

```bash
curl "http://localhost:8000/usuario/?page=1&per_page=10&usuario=jperez&fkEmpleado=uuid-empleado"
```

### Crear un rol

```bash
curl -X POST http://localhost:8000/rol/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Administrador",
    "creado_por": "uuid-admin"
  }'
```

### Asignar permiso a rol

```bash
curl -X POST http://localhost:8000/permiso_asignado/ \
  -H "Content-Type: application/json" \
  -d '{
    "fkRol": "uuid-rol",
    "fkPermiso": "uuid-permiso",
    "crear": true,
    "editar": true,
    "desactivar": false,
    "cancelar": false,
    "creado_por": "uuid-admin"
  }'
```

### Asignar rol a usuario

```bash
curl -X POST http://localhost:8000/usuario_rol/ \
  -H "Content-Type: application/json" \
  -d '{
    "fkUsuario": "uuid-usuario",
    "fkRol": "uuid-rol",
    "creado_por": "uuid-admin"
  }'
```

## 🗃️ Base de datos

- **Base de datos**: `microservices_db` (compartida)
- **Puerto del servicio**: 8000

### Tablas

- `usuario` - Información de usuarios
- `rol` - Catálogo de roles
- `permisos` - Catálogo de permisos
- `permisos_asignados` - Asignación de permisos a roles
- `usuario_rol` - Relación usuarios-roles

## 🔐 Campos de auditoría

Todos los modelos incluyen automáticamente:

- `oid` - UUID único
- `createdAt` - Fecha de creación
- `updatedAt` - Fecha de última actualización
- `creado_por` - Usuario que creó el registro
- `editado_por` - Usuario que editó el registro
- `estatus` - Estado (Activo, Inactivo, Eliminado)

## 📚 Documentación adicional

Para más detalles sobre los estándares de desarrollo seguidos en este proyecto, consulta [DEVELOPMENT_STANDARDS.md](DEVELOPMENT_STANDARDS.md)
