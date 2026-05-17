# Ejemplos de Uso de la API

Este archivo contiene ejemplos prácticos de cómo usar cada endpoint de la API.

**Nota:** Los ejemplos usan `http://localhost:8002` (puerto por defecto). Si configuraste un puerto diferente en tu archivo `.env`, ajusta la URL en consecuencia.

## Empresa

### 1. Crear una empresa
```bash
curl -X POST http://localhost:8002/empresa/ \
  -H "Content-Type: application/json" \
  -d '{
    "clave": "EMP-001",
    "nombre": "Acme Corporation",
    "folio": "FOL-2024-001",
    "urlLogo": "https://ejemplo.com/logo.png",
    "direccion": "Av. Principal 123, Ciudad",
    "telefono": "5551234567",
    "email": "contacto@acme.com",
    "creado_por": "user-123"
  }'
```

### 2. Obtener una empresa por OID
```bash
curl -X GET http://localhost:8002/empresa/123e4567-e89b-12d3-a456-426614174000
```

### 3. Listar empresas con filtros
```bash
curl -X GET "http://localhost:8002/empresa/?page=1&per_page=10&nombre=acme"
```

### 4. Actualizar una empresa
```bash
curl -X PUT http://localhost:8002/empresa/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Acme Corporation SA de CV",
    "direccion": "Nueva dirección 456",
    "editado_por": "user-123"
  }'
```

### 5. Crear múltiples empresas
```bash
curl -X POST http://localhost:8002/empresa/many \
  -H "Content-Type: application/json" \
  -d '[
    {
      "clave": "EMP-001",
      "nombre": "Empresa 1",
      "folio": "FOL-001",
      "urlLogo": "https://ejemplo.com/logo1.png",
      "direccion": "Dirección 1",
      "telefono": "5551111111",
      "email": "empresa1@ejemplo.com"
    },
    {
      "clave": "EMP-002",
      "nombre": "Empresa 2",
      "folio": "FOL-002",
      "urlLogo": "https://ejemplo.com/logo2.png",
      "direccion": "Dirección 2",
      "telefono": "5552222222",
      "email": "empresa2@ejemplo.com"
    }
  ]'
```

### 6. Actualizar múltiples empresas
```bash
curl -X PUT http://localhost:8002/empresa/many \
  -H "Content-Type: application/json" \
  -d '[
    {
      "oid": "123e4567-e89b-12d3-a456-426614174000",
      "nombre": "Nuevo Nombre 1",
      "editado_por": "user-123"
    },
    {
      "oid": "123e4567-e89b-12d3-a456-426614174001",
      "nombre": "Nuevo Nombre 2",
      "editado_por": "user-123"
    }
  ]'
```

### 7. Eliminar una empresa (soft delete)
```bash
curl -X DELETE http://localhost:8002/empresa/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{
    "editado_por": "user-123"
  }'
```

---

## Producto

### 1. Crear un producto
```bash
curl -X POST http://localhost:8002/producto/ \
  -H "Content-Type: application/json" \
  -d '{
    "clave": "PROD-001",
    "nombre": "Laptop Dell",
    "codigo_barras": "7501234567890",
    "unidadMedida": "PIEZA",
    "is_especial": false,
    "fkProveedorMarca": "prov-123",
    "creado_por": "user-123"
  }'
```

### 2. Obtener un producto por OID
```bash
curl -X GET http://localhost:8002/producto/123e4567-e89b-12d3-a456-426614174000
```

### 3. Listar productos con filtros
```bash
curl -X GET "http://localhost:8002/producto/?page=1&per_page=10&nombre=laptop&is_especial=false"
```

### 4. Actualizar un producto
```bash
curl -X PUT http://localhost:8002/producto/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Laptop Dell Inspiron 15",
    "is_especial": true,
    "editado_por": "user-123"
  }'
```

### 5. Crear múltiples productos
```bash
curl -X POST http://localhost:8002/producto/many \
  -H "Content-Type: application/json" \
  -d '[
    {
      "clave": "PROD-001",
      "nombre": "Producto 1",
      "unidadMedida": "PIEZA",
      "fkProveedorMarca": "prov-123"
    },
    {
      "clave": "PROD-002",
      "nombre": "Producto 2",
      "codigo_barras": "7501234567891",
      "unidadMedida": "KILOGRAMO",
      "fkProveedorMarca": "prov-123"
    }
  ]'
```

### 6. Eliminar un producto (soft delete)
```bash
curl -X DELETE http://localhost:8002/producto/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{
    "editado_por": "user-123"
  }'
```

---

## Sistema

### 1. Crear un sistema
```bash
curl -X POST http://localhost:8002/sistema/ \
  -H "Content-Type: application/json" \
  -d '{
    "clave": "SYS-001",
    "nombre": "Sistema Principal",
    "descripcion": "Sistema de gestión empresarial",
    "api_key": "sk_test_1234567890abcdef",
    "creado_por": "user-123"
  }'
```

### 2. Obtener un sistema por OID
```bash
curl -X GET http://localhost:8002/sistema/123e4567-e89b-12d3-a456-426614174000
```

### 3. Listar sistemas con filtros
```bash
curl -X GET "http://localhost:8002/sistema/?page=1&per_page=10&clave=SYS"
```

### 4. Actualizar un sistema
```bash
curl -X PUT http://localhost:8002/sistema/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Sistema Principal v2",
    "descripcion": "Sistema actualizado",
    "editado_por": "user-123"
  }'
```

### 5. Eliminar un sistema (soft delete)
```bash
curl -X DELETE http://localhost:8002/sistema/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{
    "editado_por": "user-123"
  }'
```

---

## Sucursal

### 1. Crear una sucursal
```bash
curl -X POST http://localhost:8002/sucursal/ \
  -H "Content-Type: application/json" \
  -d '{
    "clave": "SUC-001",
    "nombre": "Sucursal Centro",
    "folio": "FOL-SUC-001",
    "direccion": "Av. Central 456, Colonia Centro",
    "telefono": "5559876543",
    "fkEmpresa": "empresa-oid-123",
    "creado_por": "user-123"
  }'
```

### 2. Obtener una sucursal por OID
```bash
curl -X GET http://localhost:8002/sucursal/123e4567-e89b-12d3-a456-426614174000
```

### 3. Listar sucursales con filtros (por empresa)
```bash
curl -X GET "http://localhost:8002/sucursal/?fkEmpresa=empresa-oid-123&page=1&per_page=10"
```

### 4. Actualizar una sucursal
```bash
curl -X PUT http://localhost:8002/sucursal/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Sucursal Centro Histórico",
    "direccion": "Nueva dirección centro",
    "editado_por": "user-123"
  }'
```

### 5. Crear múltiples sucursales
```bash
curl -X POST http://localhost:8002/sucursal/many \
  -H "Content-Type: application/json" \
  -d '[
    {
      "clave": "SUC-001",
      "nombre": "Sucursal Norte",
      "folio": "FOL-SUC-001",
      "direccion": "Dirección Norte",
      "fkEmpresa": "empresa-oid-123"
    },
    {
      "clave": "SUC-002",
      "nombre": "Sucursal Sur",
      "folio": "FOL-SUC-002",
      "direccion": "Dirección Sur",
      "fkEmpresa": "empresa-oid-123"
    }
  ]'
```

### 6. Eliminar una sucursal (soft delete)
```bash
curl -X DELETE http://localhost:8002/sucursal/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{
    "editado_por": "user-123"
  }'
```

---

## Usando Python requests

```python
import requests

# Base URL
BASE_URL = "http://localhost:8002"

# Crear una empresa
empresa_data = {
    "clave": "EMP-001",
    "nombre": "Mi Empresa",
    "folio": "FOL-001",
    "urlLogo": "https://ejemplo.com/logo.png",
    "direccion": "Calle Principal 123",
    "telefono": "5551234567",
    "email": "contacto@empresa.com"
}

response = requests.post(f"{BASE_URL}/empresa/", json=empresa_data)
print(response.json())

# Obtener todas las empresas
response = requests.get(f"{BASE_URL}/empresa/", params={"page": 1, "per_page": 10})
print(response.json())

# Actualizar una empresa
empresa_oid = "123e4567-e89b-12d3-a456-426614174000"
update_data = {
    "nombre": "Nuevo Nombre",
    "editado_por": "user-123"
}

response = requests.put(f"{BASE_URL}/empresa/{empresa_oid}", json=update_data)
print(response.json())

# Eliminar una empresa
response = requests.delete(f"{BASE_URL}/empresa/{empresa_oid}", json={"editado_por": "user-123"})
print(response.json())
```

---

## Notas Importantes

1. **Unidades de Medida válidas:** GRAMO, KILOGRAMO, LITRO, MILILITRO, PIEZA (mayúsculas)
2. **Estatus válidos:** ACTIVO, INACTIVO, ELIMINADO, CANCELADO
3. Los campos de auditoría (`creado_por`, `editado_por`) son opcionales pero recomendados
4. Todas las operaciones de listado excluyen automáticamente registros ELIMINADOS
5. El DELETE es siempre soft delete (no elimina físicamente el registro)
