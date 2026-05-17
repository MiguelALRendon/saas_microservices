# Especificaciones Técnicas - Auth Service

**Versión:** 1.0  
**Fecha:** Marzo 2026  
**Puerto:** 8000  
**Base de datos:** microservices_db (compartida)

---

## 📋 Descripción General

El **Auth Service** es el microservicio encargado de la gestión de autenticación, usuarios, roles y permisos del sistema SaaS. Proporciona un sistema completo de Control de Acceso Basado en Roles (RBAC - Role-Based Access Control).

### Responsabilidades

- Gestión de usuarios y sus datos personales
- Administración del catálogo de roles
- Administración del catálogo de permisos
- Asignación de permisos a roles con granularidad CRUD
- Asignación de roles a usuarios

### Restricciones de Diseño

⚠️ **IMPORTANTE:**
- **NO se permiten operaciones múltiples** para Usuarios y Roles
- Los endpoints `/many` están **DESHABILITADOS** para las entidades Usuario y Rol
- Solo se pueden crear/modificar usuarios y roles de uno en uno
- Las entidades Permiso, PermisoAsignado y UsuarioRol **SÍ permiten** operaciones múltiples

---

## 🗄️ Modelos de Datos

### 1. Usuario

Gestiona la información de los usuarios del sistema.

**Tabla:** `usuario`

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| oid | String(36) | PK, UUID | Identificador único |
| usuario | String(100) | Unique, Index, Required | Nombre de usuario |
| contraseña | String(255) | Required | Contraseña encriptada (Argon2) |
| fkSistema | String(36) | Index, Required | Referencia a Sistema (catalogues_service) |
| fkEmpleado | String(36) | Index, Required | Referencia a Empleado (branch_service) - incluye empresa y sucursal |
| createdAt | DateTime | Auto | Fecha de creación |
| updatedAt | DateTime | Auto | Fecha de actualización |
| creado_por | String(36) | Opcional | Usuario que creó el registro |
| editado_por | String(36) | Opcional | Usuario que editó el registro |
| estatus | Enum | Default: ACTIVO | Estado del registro |

**Relaciones:**
- `usuario_roles` → UsuarioRol (1:N)

**Índices:**
- `usuario` (unique)
- `fkSistema`
- `fkEmpleado`

**Nota:** Los datos personales (nombres, apellidos, email, teléfono) y la relación empresa/sucursal se obtienen a través de `fkEmpleado` del `branch_service`.

### 2. Rol

Catálogo de roles disponibles en el sistema.

**Tabla:** `rol`

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| oid | String(36) | PK, UUID | Identificador único |
| nombre | String(100) | Unique, Index, Required | Nombre del rol |
| createdAt | DateTime | Auto | Fecha de creación |
| updatedAt | DateTime | Auto | Fecha de actualización |
| creado_por | String(36) | Opcional | Usuario que creó el registro |
| editado_por | String(36) | Opcional | Usuario que editó el registro |
| estatus | Enum | Default: ACTIVO | Estado del registro |

**Relaciones:**
- `usuario_roles` → UsuarioRol (1:N)
- `permisos_asignados` → PermisoAsignado (1:N)

**Índices:**
- `nombre` (unique)

### 3. Permiso

Catálogo de permisos disponibles en el sistema.

**Tabla:** `permisos`

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| oid | String(36) | PK, UUID | Identificador único |
| clave | String(25) | Unique, Index, Required | Clave única del permiso |
| nombre | String(100) | Index, Required | Nombre descriptivo |
| permiso | String(100) | Index, Required | Identificador del permiso |
| createdAt | DateTime | Auto | Fecha de creación |
| updatedAt | DateTime | Auto | Fecha de actualización |
| creado_por | String(36) | Opcional | Usuario que creó el registro |
| editado_por | String(36) | Opcional | Usuario que editó el registro |
| estatus | Enum | Default: ACTIVO | Estado del registro |

**Relaciones:**
- `permisos_asignados` → PermisoAsignado (1:N)

**Índices:**
- `clave` (unique)
- `nombre`
- `permiso`

### 4. PermisoAsignado

Asignación de permisos a roles con control granular CRUD.

**Tabla:** `permisos_asignados`

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| oid | String(36) | PK, UUID | Identificador único |
| fkPermiso | String(36) | FK, Index, Required | Referencia a Permiso |
| fkRol | String(36) | FK, Index, Required | Referencia a Rol |
| crear | Boolean | Default: False | Permiso para crear |
| editar | Boolean | Default: False | Permiso para editar |
| desactivar | Boolean | Default: False | Permiso para desactivar |
| cancelar | Boolean | Default: False | Permiso para cancelar |
| createdAt | DateTime | Auto | Fecha de creación |
| updatedAt | DateTime | Auto | Fecha de actualización |
| creado_por | String(36) | Opcional | Usuario que creó el registro |
| editado_por | String(36) | Opcional | Usuario que editó el registro |
| estatus | Enum | Default: ACTIVO | Estado del registro |

**Restricciones:**
- Índice único compuesto: `(fkRol, fkPermiso)` - Un permiso solo puede asignarse una vez a un rol

**Relaciones:**
- `permiso` → Permiso (N:1)
- `rol` → Rol (N:1)

### 5. UsuarioRol

Relación muchos a muchos entre usuarios y roles.

**Tabla:** `usuario_rol`

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| oid | String(36) | PK, UUID | Identificador único |
| fkUsuario | String(36) | FK, Index, Required | Referencia a Usuario |
| fkRol | String(36) | FK, Index, Required | Referencia a Rol |
| createdAt | DateTime | Auto | Fecha de creación |
| updatedAt | DateTime | Auto | Fecha de actualización |
| creado_por | String(36) | Opcional | Usuario que creó el registro |
| editado_por | String(36) | Opcional | Usuario que editó el registro |
| estatus | Enum | Default: ACTIVO | Estado del registro |

**Restricciones:**
- Índice único compuesto: `(fkUsuario, fkRol)` - Un usuario no puede tener el mismo rol dos veces

**Relaciones:**
- `usuario` → Usuario (N:1)
- `rol` → Rol (N:1)

---

## 📡 Endpoints Disponibles

### Usuario (`/usuario`)

#### ✅ Endpoints Habilitados

| Método | Endpoint | Descripción | Códigos HTTP |
|--------|----------|-------------|--------------|
| GET | `/usuario/<oid>` | Obtener usuario por OID | 200, 404, 500 |
| GET | `/usuario/` | Listar usuarios (paginado) | 200, 500 |
| POST | `/usuario/` | Crear un usuario | 201, 400, 500 |
| PUT | `/usuario/<oid>` | Actualizar un usuario | 200, 400, 404, 500 |
| DELETE | `/usuario/<oid>` | Eliminar usuario (soft delete) | 200, 404, 500 |

#### ❌ Endpoints Deshabilitados

- `POST /usuario/many` - **NO IMPLEMENTADO**
- `PUT /usuario/many` - **NO IMPLEMENTADO**

**Filtros disponibles (GET):** `usuario`, `nombres`, `email`, `fkEmpresa`, `fkSucursal`

**Parámetros de paginación:** `page` (default: 1), `per_page` (default: 10)

### Rol (`/rol`)

#### ✅ Endpoints Habilitados

| Método | Endpoint | Descripción | Códigos HTTP |
|--------|----------|-------------|--------------|
| GET | `/rol/<oid>` | Obtener rol por OID | 200, 404, 500 |
| GET | `/rol/` | Listar roles (paginado) | 200, 500 |
| POST | `/rol/` | Crear un rol | 201, 400, 500 |
| PUT | `/rol/<oid>` | Actualizar un rol | 200, 400, 404, 500 |
| DELETE | `/rol/<oid>` | Eliminar rol (soft delete) | 200, 404, 500 |

#### ❌ Endpoints Deshabilitados

- `POST /rol/many` - **NO IMPLEMENTADO**
- `PUT /rol/many` - **NO IMPLEMENTADO**

**Filtros disponibles (GET):** `nombre`

**Parámetros de paginación:** `page` (default: 1), `per_page` (default: 10)

### Permiso (`/permiso`)

#### ✅ Todos los Endpoints Habilitados

| Método | Endpoint | Descripción | Códigos HTTP |
|--------|----------|-------------|--------------|
| GET | `/permiso/<oid>` | Obtener permiso por OID | 200, 404, 500 |
| GET | `/permiso/` | Listar permisos (paginado) | 200, 500 |
| POST | `/permiso/` | Crear un permiso | 201, 400, 500 |
| POST | `/permiso/many` | Crear múltiples permisos | 201, 400, 500 |
| PUT | `/permiso/<oid>` | Actualizar un permiso | 200, 400, 404, 500 |
| PUT | `/permiso/many` | Actualizar múltiples permisos | 200, 400, 500 |
| DELETE | `/permiso/<oid>` | Eliminar permiso (soft delete) | 200, 404, 500 |

**Filtros disponibles (GET):** `clave`, `nombre`, `permiso`

**Parámetros de paginación:** `page` (default: 1), `per_page` (default: 10)

### PermisoAsignado (`/permiso_asignado`)

#### ✅ Todos los Endpoints Habilitados

| Método | Endpoint | Descripción | Códigos HTTP |
|--------|----------|-------------|--------------|
| GET | `/permiso_asignado/<oid>` | Obtener permiso asignado por OID | 200, 404, 500 |
| GET | `/permiso_asignado/` | Listar permisos asignados (paginado) | 200, 500 |
| POST | `/permiso_asignado/` | Crear un permiso asignado | 201, 400, 500 |
| POST | `/permiso_asignado/many` | Crear múltiples permisos asignados | 201, 400, 500 |
| PUT | `/permiso_asignado/<oid>` | Actualizar un permiso asignado | 200, 400, 404, 500 |
| PUT | `/permiso_asignado/many` | Actualizar múltiples permisos asignados | 200, 400, 500 |
| DELETE | `/permiso_asignado/<oid>` | Eliminar permiso asignado (soft delete) | 200, 404, 500 |

**Filtros disponibles (GET):** `fkRol`, `fkPermiso`

**Parámetros de paginación:** `page` (default: 1), `per_page` (default: 10)

### UsuarioRol (`/usuario_rol`)

#### ✅ Todos los Endpoints Habilitados

| Método | Endpoint | Descripción | Códigos HTTP |
|--------|----------|-------------|--------------|
| GET | `/usuario_rol/<oid>` | Obtener usuario-rol por OID | 200, 404, 500 |
| GET | `/usuario_rol/` | Listar usuario-roles (paginado) | 200, 500 |
| POST | `/usuario_rol/` | Crear una asignación usuario-rol | 201, 400, 500 |
| POST | `/usuario_rol/many` | Crear múltiples asignaciones | 201, 400, 500 |
| PUT | `/usuario_rol/<oid>` | Actualizar una asignación | 200, 400, 404, 500 |
| PUT | `/usuario_rol/many` | Actualizar múltiples asignaciones | 200, 400, 500 |
| DELETE | `/usuario_rol/<oid>` | Eliminar asignación (soft delete) | 200, 404, 500 |

**Filtros disponibles (GET):** `fkUsuario`, `fkRol`

**Parámetros de paginación:** `page` (default: 1), `per_page` (default: 10)

---

## 🔐 Reglas de Negocio

### Usuarios

1. **Unicidad:** El campo `usuario` debe ser único en el sistema
2. **Campos obligatorios:** `usuario`, `contraseña`, `apellidoPaterno`, `apellidoMaterno`, `nombres`, `fkEmpresa`, `fkSucursal`, `fkSistema`
3. **Seguridad:** La contraseña nunca se incluye en las respuestas de serialización
4. **Creación:** Solo se puede crear un usuario a la vez
5. **Modificación:** Solo se puede actualizar un usuario a la vez
6. **Eliminación:** Soft delete - se marca como ELIMINADO
7. **Referencias:** Debe existir la Empresa, Sucursal y Sistema referenciados

### Roles

1. **Unicidad:** El campo `nombre` debe ser único en el sistema
2. **Campos obligatorios:** `nombre`
3. **Creación:** Solo se puede crear un rol a la vez
4. **Modificación:** Solo se puede actualizar un rol a la vez
5. **Eliminación:** Soft delete - se marca como ELIMINADO
6. **Dependencias:** Al eliminar un rol, se deben considerar las asignaciones existentes

### Permisos

1. **Unicidad:** El campo `clave` debe ser único en el sistema
2. **Campos obligatorios:** `clave`, `nombre`, `permiso`
3. **Creación múltiple:** Se permite crear múltiples permisos en una sola operación
4. **Modificación múltiple:** Se permite actualizar múltiples permisos en una sola operación
5. **Eliminación:** Soft delete - se marca como ELIMINADO

### Permisos Asignados

1. **Unicidad:** La combinación `(fkRol, fkPermiso)` debe ser única
2. **Campos obligatorios:** `fkRol`, `fkPermiso`
3. **Permisos CRUD:** Por defecto todos los permisos CRUD están en `false`
4. **Granularidad:** Se puede controlar individualmente: `crear`, `editar`, `desactivar`, `cancelar`
5. **Creación múltiple:** Se permite asignar múltiples permisos a roles en una sola operación
6. **Modificación múltiple:** Se permite actualizar múltiples asignaciones en una sola operación
7. **Validación:** Debe existir el rol y el permiso antes de crear la asignación

### Usuario-Rol

1. **Unicidad:** La combinación `(fkUsuario, fkRol)` debe ser única
2. **Campos obligatorios:** `fkUsuario`, `fkRol`
3. **Roles múltiples:** Un usuario puede tener múltiples roles
4. **Creación múltiple:** Se permite asignar múltiples roles a usuarios en una sola operación
5. **Modificación múltiple:** Se permite actualizar múltiples asignaciones en una sola operación
6. **Validación:** Debe existir el usuario y el rol antes de crear la asignación

---

## 📤 Formato de Respuestas

### Respuesta Exitosa - Objeto Único

```json
{
  "oid": "123e4567-e89b-12d3-a456-426614174000",
  "createdAt": "2026-03-14T10:30:00",
  "updatedAt": "2026-03-14T10:30:00",
  "creado_por": "user-oid-123",
  "editado_por": null,
  "estatus": "Activo",
  "usuario": "jperez",
  "apellidoPaterno": "Pérez",
  "apellidoMaterno": "González",
  "nombres": "Juan Carlos",
  "telefono": "5551234567",
  "email": "jperez@example.com",
  "fkEmpresa": "empresa-oid-456",
  "fkSucursal": "sucursal-oid-789",
  "fkSistema": "sistema-oid-101"
}
```

### Respuesta Exitosa - Lista Paginada

```json
{
  "data": [
    { /* objeto 1 */ },
    { /* objeto 2 */ }
  ],
  "total": 50,
  "page": 1,
  "per_page": 10,
  "pages": 5
}
```

### Respuesta de Creación Múltiple

```json
{
  "created": 3,
  "data": [
    { /* objeto 1 */ },
    { /* objeto 2 */ },
    { /* objeto 3 */ }
  ],
  "errors": [
    {
      "index": 4,
      "errors": ["La clave ya existe"]
    }
  ]
}
```

### Respuesta de Error

```json
{
  "errors": [
    "usuario es requerido",
    "contraseña es requerida"
  ]
}
```

**Nota:** TODAS las respuestas de error usan el formato `{"errors": [...]}` (array), nunca `{"error": "..."}` (singular).

---

## 🔄 Flujos de Trabajo Comunes

### 1. Registro de Nuevo Usuario

```
1. POST /usuario/
   → Crear usuario con datos básicos y referencias

2. POST /usuario_rol/many
   → Asignar uno o más roles al usuario

3. GET /usuario/<oid>
   → Verificar datos del usuario creado
```

### 2. Configuración de Rol

```
1. POST /rol/
   → Crear un nuevo rol

2. POST /permiso_asignado/many
   → Asignar múltiples permisos al rol con configuración CRUD

3. GET /permiso_asignado/?fkRol=<rol_oid>
   → Verificar permisos asignados al rol
```

### 3. Actualización de Permisos de Usuario

```
1. GET /usuario_rol/?fkUsuario=<usuario_oid>
   → Obtener roles actuales del usuario

2. DELETE /usuario_rol/<oid>
   → Remover roles no deseados

3. POST /usuario_rol/many
   → Agregar nuevos roles al usuario
```

---

## 🔗 Dependencias con Otros Microservicios

### Catalogues Service (Puerto 8002)

- **Empresa:** `fkEmpresa` en Usuario
- **Sistema:** `fkSistema` en Usuario

### Branch Service (Puerto 8001)

- **Sucursal:** `fkSucursal` en Usuario

**Nota:** Las referencias son por OID (UUID) y se validan a nivel de aplicación. No hay foreign keys físicas en la base de datos para permitir independencia entre microservicios.

---

## ⚙️ Configuración

### Variables de Entorno Requeridas

```bash
# Seguridad
SECRET_KEY=<clave-secreta>
JWT_SECRET_KEY=<clave-jwt-secreta>

# Base de Datos
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/microservices_db

# Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=False
BASE_URL=http://localhost:8000

# URLs de Microservicios
AUTH_SERVICE_URL=http://localhost:8000
CATALOGUES_SERVICE_URL=http://localhost:8002
BRANCH_SERVICE_URL=http://localhost:8001
INVENTORY_SERVICE_URL=http://localhost:8003
SALES_SERVICE_URL=http://localhost:8004
SUPPLIER_SERVICE_URL=http://localhost:8005
VALIDATION_SERVICE_URL=http://localhost:8006
```

---

## 🚀 Inicialización

### Orden de Ejecución

1. Configurar variables de entorno (`.env`)
2. Iniciar servicio de base de datos MySQL
3. Ejecutar `python run.py`
4. El servidor creará las tablas automáticamente si no existen

### Tablas Creadas

- `usuario`
- `rol`
- `permisos`
- `permisos_asignados`
- `usuario_rol`

---

## 📊 Auditoría

Todos los registros incluyen campos de auditoría:

- `oid`: Identificador único UUID
- `createdAt`: Timestamp de creación (UTC)
- `updatedAt`: Timestamp de última modificación (UTC)
- `creado_por`: OID del usuario que creó el registro
- `editado_por`: OID del usuario que realizó la última modificación
- `estatus`: Estado del registro (Activo, Inactivo, Eliminado)

### Soft Delete

- Los registros NUNCA se eliminan físicamente
- La eliminación marca el registro con `estatus = "Eliminado"`
- Los registros eliminados se excluyen automáticamente de todas las consultas GET
- Se mantiene el historial completo para auditoría

---

## 📝 Notas Adicionales

1. **Paginación:** Todos los endpoints de listado soportan paginación mediante `page` y `per_page`

2. **Filtrado:** Los endpoints de listado permiten filtrado por campos específicos vía query parameters

3. **Transacciones:** Todas las operaciones de escritura usan transacciones con rollback automático en caso de error

4. **Validación:** La validación de datos se realiza a nivel de schema antes de cualquier operación en base de datos

5. **Seguridad:** Las contraseñas se almacenan (idealmente encriptadas) y nunca se exponen en las respuestas

6. **Unicidad:** Se validan restricciones de unicidad antes de crear o actualizar registros

---

**Última actualización:** Marzo 14, 2026  
**Mantenido por:** Equipo de Desarrollo SaaS
