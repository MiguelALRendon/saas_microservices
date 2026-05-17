# Catalogues Service

Microservicio de catálogos: empresas, productos, sistemas y sucursales.

## Modelos incluidos:
- Empresa
- Producto
- Sistema
- Sucursal

## Base de datos
- Base de datos: `catalogues_service_db`
- Tablas compartidas: `Base`, `BaseContactoObject`
- Enums: `UnidadMedida`, `BaseObjectEstatus`

## Instalación

```bash
pip install -r requirements.txt
```

## Configuración

1. Copiar `.env.example` a `.env` y configurar las variables de entorno:
```bash
# Application Settings
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database Configuration
DATABASE_URL=mysql+pymysql://usuario:password@localhost:3306/catalogues_service_db

# Server Configuration
HOST=0.0.0.0
PORT=8002
DEBUG=False
BASE_URL=http://localhost:8002

# Microservices URLs (opcional si interactúas con otros servicios)
AUTH_SERVICE_URL=http://localhost:8000
CATALOGUES_SERVICE_URL=http://localhost:8002
# ... otros servicios
```

2. Ejecutar la aplicación:
```bash
python run.py
```

La API estará disponible en `http://localhost:8002` (o el puerto configurado en PORT)

## Documentación de la API

Todas las entidades (Empresa, Producto, Sistema, Sucursal) comparten la misma estructura de endpoints:

### Endpoints Disponibles

#### 1. GET /{entidad}/{oid}
Obtiene un registro por su OID.

**Respuesta exitosa (200):**
```json
{
  "oid": "uuid",
  "clave": "string",
  "nombre": "string",
  "estatus": "Activo",
  "createdAt": "2024-01-01T00:00:00",
  "updatedAt": "2024-01-01T00:00:00",
  ...
}
```

**Ejemplos:**
- `GET /empresa/123e4567-e89b-12d3-a456-426614174000`
- `GET /producto/123e4567-e89b-12d3-a456-426614174000`
- `GET /sistema/123e4567-e89b-12d3-a456-426614174000`
- `GET /sucursal/123e4567-e89b-12d3-a456-426614174000`

---

#### 2. GET /{entidad}/
Obtiene listado paginado y filtrado de registros.

**Query Parameters:**
- `page`: Número de página (default: 1)
- `per_page`: Registros por página (default: 10)
- Filtros específicos por entidad (ej: `clave`, `nombre`, `email`, etc.)

**Respuesta exitosa (200):**
```json
{
  "data": [...],
  "total": 100,
  "page": 1,
  "per_page": 10,
  "pages": 10
}
```

**Ejemplos:**
- `GET /empresa/?page=1&per_page=20&nombre=acme`
- `GET /producto/?clave=PROD-001&is_especial=true`
- `GET /sucursal/?fkEmpresa=123e4567-e89b-12d3-a456-426614174000`

**Nota:** Solo devuelve registros con estatus != ELIMINADO

---

#### 3. POST /{entidad}/
Crea un nuevo registro.

**Request Body (Empresa):**
```json
{
  "clave": "EMP-001",
  "nombre": "Mi Empresa",
  "folio": "FOL-001",
  "urlLogo": "https://ejemplo.com/logo.png",
  "direccion": "Calle Principal 123",
  "telefono": "5551234567",
  "email": "contacto@empresa.com",
  "creado_por": "usuario-oid"
}
```

**Request Body (Producto):**
```json
{
  "clave": "PROD-001",
  "nombre": "Producto 1",
  "codigo_barras": "7501234567890",
  "unidadMedida": "PIEZA",
  "is_especial": false,
  "fkProveedorMarca": "proveedor-oid",
  "creado_por": "usuario-oid"
}
```

**Request Body (Sistema):**
```json
{
  "clave": "SYS-001",
  "nombre": "Sistema Principal",
  "descripcion": "Sistema de gestión",
  "api_key": "api-key-unica",
  "creado_por": "usuario-oid"
}
```

**Request Body (Sucursal):**
```json
{
  "clave": "SUC-001",
  "nombre": "Sucursal Centro",
  "folio": "FOL-SUC-001",
  "direccion": "Avenida Central 456",
  "telefono": "5559876543",
  "fkEmpresa": "empresa-oid",
  "creado_por": "usuario-oid"
}
```

**Respuesta exitosa (201):** Registro creado con todos sus campos

---

#### 4. POST /{entidad}/many
Crea múltiples registros simultáneamente.

**Request Body:**
```json
[
  {
    "clave": "EMP-001",
    "nombre": "Empresa 1",
    ...
  },
  {
    "clave": "EMP-002",
    "nombre": "Empresa 2",
    ...
  }
]
```

**Respuesta exitosa (201):**
```json
{
  "created": 2,
  "data": [...],
  "errors": []
}
```

**Nota:** Los errores individuales se reportan en el array `errors` con el índice del registro problemático.

---

#### 5. PUT /{entidad}/{oid}
Actualiza un registro existente.

**Request Body (campos parciales):**
```json
{
  "nombre": "Nuevo Nombre",
  "direccion": "Nueva Dirección",
  "editado_por": "usuario-oid"
}
```

**Respuesta exitosa (200):** Registro actualizado completo

---

#### 6. PUT /{entidad}/many
Actualiza múltiples registros simultáneamente.

**Request Body:**
```json
[
  {
    "oid": "registro-oid-1",
    "nombre": "Nuevo Nombre 1",
    "editado_por": "usuario-oid"
  },
  {
    "oid": "registro-oid-2",
    "nombre": "Nuevo Nombre 2",
    "editado_por": "usuario-oid"
  }
]
```

**Respuesta exitosa (200):**
```json
{
  "updated": 2,
  "data": [...],
  "errors": []
}
```

---

#### 7. DELETE /{entidad}/{oid}
Realiza un soft delete (marca el registro como ELIMINADO).

**Request Body (opcional):**
```json
{
  "editado_por": "usuario-oid"
}
```

**Respuesta exitosa (200):**
```json
{
  "message": "Empresa eliminada exitosamente"
}
```

**Nota:** No elimina físicamente el registro, solo cambia su estatus a ELIMINADO.

---

## Campos Comunes (BaseObject)

Todos los modelos heredan estos campos:
- `oid`: UUID único (primary key)
- `createdAt`: Fecha de creación
- `updatedAt`: Fecha de última modificación
- `creado_por`: OID del usuario que creó el registro
- `editado_por`: OID del usuario que editó el registro por última vez
- `estatus`: ACTIVO | INACTIVO | ELIMINADO | CANCELADO

## Validaciones

### Empresa
- `clave`: Unique, requerida
- `nombre`: Requerido
- `folio`: Requerido
- `urlLogo`: Requerido
- `direccion`: Requerida
- `telefono`: Opcional
- `email`: Opcional

### Producto
- `clave`: Unique, requerida
- `nombre`: Requerido
- `codigo_barras`: Unique (si se proporciona), opcional
- `unidadMedida`: Requerida (GRAMO, KILOGRAMO, LITRO, MILILITRO, PIEZA)
- `is_especial`: Boolean, default: false
- `fkProveedorMarca`: Requerido

### Sistema
- `clave`: Unique, requerida
- `nombre`: Requerido
- `descripcion`: Opcional
- `api_key`: Unique, requerida

### Sucursal
- `clave`: Unique, requerida
- `nombre`: Requerido
- `folio`: Requerido
- `direccion`: Requerida
- `telefono`: Opcional
- `fkEmpresa`: Requerido (Foreign Key a Empresa)

## Códigos de Respuesta HTTP

- `200 OK`: Operación exitosa (GET, PUT, DELETE)
- `201 Created`: Recurso creado exitosamente (POST)
- `400 Bad Request`: Error en validación de datos
- `404 Not Found`: Recurso no encontrado
- `500 Internal Server Error`: Error del servidor

## Notas Importantes

1. **Soft Delete**: El DELETE no elimina físicamente los registros, solo los marca como ELIMINADOS.
2. **Filtrado Automático**: Todos los GET filtran automáticamente los registros con estatus ELIMINADO.
3. **Paginación**: Los listados soportan paginación mediante `page` y `per_page`.
4. **Validación de Claves Únicas**: Las claves deben ser únicas por entidad.
5. **Auditoría**: Todos los registros guardan quién los creó y quién los editó por última vez.

