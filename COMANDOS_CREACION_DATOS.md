# Comandos para Poblar la Base de Datos - Microservicios SaaS

Este documento contiene los comandos de PowerShell testeados para crear entidades en los diferentes microservicios hasta llegar a crear un Usuario completo con toda su información.

## Orden de Creación

1. Sistema (Catalogues Service)
2. Empresa (Catalogues Service)
3. Sucursal (Catalogues Service)
4. Cargo (Branch Service)
5. Empleado (Branch Service)
6. Permiso (Auth Service)
7. Rol (Auth Service)
8. PermisoAsignado (Auth Service)
9. Usuario (Auth Service)
10. UsuarioRol (Auth Service)

---

## 1. Crear Sistema

**Servicio:** Catalogues Service (Puerto 8002)  
**Endpoint:** POST /sistema/

```powershell
$timestamp = Get-Date -Format "HHmmss"
$body = @{
    clave = "SYS$timestamp"
    nombre = "Sistema Principal"
    descripcion = "Sistema de gestion empresarial"
    api_key = "api-key-sistema-$timestamp"
}
$sistema = Invoke-RestMethod -Uri "http://localhost:8002/sistema/" -Method POST -Body ($body | ConvertTo-Json) -ContentType "application/json"
Write-Host "Sistema OID: $($sistema.oid)"
```

**Verificar:**
```powershell
$sistemaOid = "<OID del sistema creado>"
Invoke-RestMethod -Uri "http://localhost:8002/sistema/$sistemaOid" -Method GET
```

---

## 2. Crear Empresa

**Servicio:** Catalogues Service (Puerto 8002)  
**Endpoint:** POST /empresa/

```powershell
$timestamp = Get-Date -Format "HHmmss"
$body = @{
    clave = "EMP$timestamp"
    nombre = "Mi Empresa SA de CV"
    folio = "FOLIO-EMP-$timestamp"
    urlLogo = "https://ejemplo.com/logo.png"
    direccion = "Av. Principal 123, Ciudad, Estado"
    telefono = "5551234567"
    email = "contacto@miempresa.com"
}
$empresa = Invoke-RestMethod -Uri "http://localhost:8002/empresa/" -Method POST -Body ($body | ConvertTo-Json) -ContentType "application/json"
Write-Host "Empresa OID: $($empresa.oid)"
```

**Verificar:**
```powershell
$empresaOid = "<OID de la empresa creada>"
Invoke-RestMethod -Uri "http://localhost:8002/empresa/$empresaOid" -Method GET
```

---

## 3. Crear Sucursal

**Servicio:** Catalogues Service (Puerto 8002)  
**Endpoint:** POST /sucursal/  
**Dependencias:** Requiere OID de Empresa

```powershell
$empresaOid = "<OID de la empresa creada>"
$timestamp = Get-Date -Format "HHmmss"
$body = @{
    clave = "SUC$timestamp"
    nombre = "Sucursal Centro"
    folio = "FOLIO-SUC-$timestamp"
    direccion = "Calle Centro 456, Ciudad, Estado"
    telefono = "5557654321"
    fkEmpresa = $empresaOid
}
$sucursal = Invoke-RestMethod -Uri "http://localhost:8002/sucursal/" -Method POST -Body ($body | ConvertTo-Json) -ContentType "application/json"
Write-Host "Sucursal OID: $($sucursal.oid)"
```

**Verificar:**
```powershell
$sucursalOid = "<OID de la sucursal creada>"
Invoke-RestMethod -Uri "http://localhost:8002/sucursal/$sucursalOid" -Method GET
```

---

## 4. Crear Cargo

**Servicio:** Branch Service (Puerto 8001)  
**Endpoint:** POST /cargo/

```powershell
$timestamp = Get-Date -Format "HHmmss"
$body = @{
    clave = "CARGO$timestamp"
    nombre = "Gerente"
}
$cargo = Invoke-RestMethod -Uri "http://localhost:8001/cargo/" -Method POST -Body ($body | ConvertTo-Json) -ContentType "application/json"
Write-Host "Cargo OID: $($cargo.oid)"
```

**Verificar:**
```powershell
$cargoOid = "<OID del cargo creado>"
Invoke-RestMethod -Uri "http://localhost:8001/cargo/$cargoOid" -Method GET
```

---

## 5. Crear Empleado

**Servicio:** Branch Service (Puerto 8001)  
**Endpoint:** POST /empleado/  
**Dependencias:** Requiere OID de Empresa, Sucursal y Cargo

```powershell
$empresaOid = "<OID de la empresa creada>"
$sucursalOid = "<OID de la sucursal creada>"
$cargoOid = "<OID del cargo creado>"
$timestamp = Get-Date -Format "HHmmss"
$body = @{
    nombres = "Juan Carlos"
    apellido_paterno = "Perez"
    apellido_materno = "Lopez"
    curp = "PELJ90010$timestamp"
    rfc = "PELJ90$timestamp"
    fecha_contratacion = "2024-01-15"
    telefono = "5559876543"
    email = "juan.perez$timestamp@miempresa.com"
    fkEmpresa = $empresaOid
    fkSucursal = $sucursalOid
    fkCargo = $cargoOid
}
$empleado = Invoke-RestMethod -Uri "http://localhost:8001/empleado/" -Method POST -Body ($body | ConvertTo-Json) -ContentType "application/json"
Write-Host "Empleado OID: $($empleado.oid)"
```

**Verificar:**
```powershell
$empleadoOid = "<OID del empleado creado>"
Invoke-RestMethod -Uri "http://localhost:8001/empleado/$empleadoOid" -Method GET
```

---

## 6. Crear Permiso

**Servicio:** Auth Service (Puerto 8000)  
**Endpoint:** POST /permiso/

```powershell
$timestamp = Get-Date -Format "HHmmss"
$body = @{
    clave = "PERM$timestamp"
    nombre = "Ver Dashboard"
    permiso = "dashboard.view"
}
$permiso = Invoke-RestMethod -Uri "http://localhost:8000/permiso/" -Method POST -Body ($body | ConvertTo-Json) -ContentType "application/json"
Write-Host "Permiso OID: $($permiso.oid)"
```

**Verificar:**
```powershell
$permisoOid = "<OID del permiso creado>"
Invoke-RestMethod -Uri "http://localhost:8000/permiso/$permisoOid" -Method GET
```

---

## 7. Crear Rol

**Servicio:** Auth Service (Puerto 8000)  
**Endpoint:** POST /rol/

```powershell
$timestamp = Get-Date -Format "HHmmss"
$body = @{
    nombre = "Administrador$timestamp"
}
$rol = Invoke-RestMethod -Uri "http://localhost:8000/rol/" -Method POST -Body ($body | ConvertTo-Json) -ContentType "application/json"
Write-Host "Rol OID: $($rol.oid)"
```

**Verificar:**
```powershell
$rolOid = "<OID del rol creado>"
Invoke-RestMethod -Uri "http://localhost:8000/rol/$rolOid" -Method GET
```

---

## 8. Crear PermisoAsignado

**Servicio:** Auth Service (Puerto 8000)  
**Endpoint:** POST /permiso_asignado/  
**Dependencias:** Requiere OID de Permiso y Rol

```powershell
$permisoOid = "<OID del permiso creado>"
$rolOid = "<OID del rol creado>"
$body = @{
    fkPermiso = $permisoOid
    fkRol = $rolOid
    crear = $true
    editar = $true
    desactivar = $true
    cancelar = $false
}
$permisoAsignado = Invoke-RestMethod -Uri "http://localhost:8000/permiso_asignado/" -Method POST -Body ($body | ConvertTo-Json) -ContentType "application/json"
Write-Host "PermisoAsignado OID: $($permisoAsignado.oid)"
```

**Verificar:**
```powershell
$permisoAsignadoOid = "<OID del permiso asignado creado>"
Invoke-RestMethod -Uri "http://localhost:8000/permiso_asignado/$permisoAsignadoOid" -Method GET
```

---

## 9. Crear Usuario

**Servicio:** Auth Service (Puerto 8000)  
**Endpoint:** POST /usuario/  
**Dependencias:** Requiere OID de Sistema y Empleado

**IMPORTANTE:** El campo `contraseña` contiene tilde (ñ) y requiere codificación UTF-8 explícita.

```powershell
$sistemaOid = "<OID del sistema creado>"
$empleadoOid = "<OID del empleado creado>"
$timestamp = Get-Date -Format "HHmmss"
$jsonString = "{`"usuario`":`"jperez$timestamp`",`"contraseña`":`"Pass123`",`"fkSistema`":`"$sistemaOid`",`"fkEmpleado`":`"$empleadoOid`"}"
$bytes = [System.Text.Encoding]::UTF8.GetBytes($jsonString)
$usuario = Invoke-RestMethod -Uri "http://localhost:8000/usuario/" -Method POST -Body $bytes -ContentType "application/json; charset=utf-8"
Write-Host "Usuario OID: $($usuario.oid)"
```

**Verificar:**
```powershell
$usuarioOid = "<OID del usuario creado>"
$usuario = Invoke-RestMethod -Uri "http://localhost:8000/usuario/$usuarioOid" -Method GET
$usuario | ConvertTo-Json -Depth 10
```

---

## 10. Crear UsuarioRol

**Servicio:** Auth Service (Puerto 8000)  
**Endpoint:** POST /usuario_rol/  
**Dependencias:** Requiere OID de Usuario y Rol

```powershell
$usuarioOid = "<OID del usuario creado>"
$rolOid = "<OID del rol creado>"
$body = @{
    fkUsuario = $usuarioOid
    fkRol = $rolOid
}
$usuarioRol = Invoke-RestMethod -Uri "http://localhost:8000/usuario_rol/" -Method POST -Body ($body | ConvertTo-Json) -ContentType "application/json"
Write-Host "UsuarioRol OID: $($usuarioRol.oid)"
```

**Verificar:**
```powershell
$usuarioRolOid = "<OID del usuario_rol creado>"
Invoke-RestMethod -Uri "http://localhost:8000/usuario_rol/$usuarioRolOid" -Method GET
```

---

## Script Completo de Creación

A continuación un script que crea todos los objetos en orden con sus dependencias:

```powershell
# 1. Sistema
$timestamp = Get-Date -Format "HHmmss"
$body = @{ clave = "SYS$timestamp"; nombre = "Sistema Principal"; descripcion = "Sistema de gestion empresarial"; api_key = "api-key-sistema-$timestamp" }
$sistema = Invoke-RestMethod -Uri "http://localhost:8002/sistema/" -Method POST -Body ($body | ConvertTo-Json) -ContentType "application/json"
Write-Host "✓ Sistema OID: $($sistema.oid)"

# 2. Empresa
$timestamp = Get-Date -Format "HHmmss"
$body = @{ clave = "EMP$timestamp"; nombre = "Mi Empresa SA de CV"; folio = "FOLIO-EMP-$timestamp"; urlLogo = "https://ejemplo.com/logo.png"; direccion = "Av. Principal 123, Ciudad, Estado"; telefono = "5551234567"; email = "contacto@miempresa.com" }
$empresa = Invoke-RestMethod -Uri "http://localhost:8002/empresa/" -Method POST -Body ($body | ConvertTo-Json) -ContentType "application/json"
Write-Host "✓ Empresa OID: $($empresa.oid)"

# 3. Sucursal
$timestamp = Get-Date -Format "HHmmss"
$body = @{ clave = "SUC$timestamp"; nombre = "Sucursal Centro"; folio = "FOLIO-SUC-$timestamp"; direccion = "Calle Centro 456, Ciudad, Estado"; telefono = "5557654321"; fkEmpresa = $empresa.oid }
$sucursal = Invoke-RestMethod -Uri "http://localhost:8002/sucursal/" -Method POST -Body ($body | ConvertTo-Json) -ContentType "application/json"
Write-Host "✓ Sucursal OID: $($sucursal.oid)"

# 4. Cargo
$timestamp = Get-Date -Format "HHmmss"
$body = @{ clave = "CARGO$timestamp"; nombre = "Gerente" }
$cargo = Invoke-RestMethod -Uri "http://localhost:8001/cargo/" -Method POST -Body ($body | ConvertTo-Json) -ContentType "application/json"
Write-Host "✓ Cargo OID: $($cargo.oid)"

# 5. Empleado
$timestamp = Get-Date -Format "HHmmss"
$body = @{ nombres = "Juan Carlos"; apellido_paterno = "Perez"; apellido_materno = "Lopez"; curp = "PELJ90010$timestamp"; rfc = "PELJ90$timestamp"; fecha_contratacion = "2024-01-15"; telefono = "5559876543"; email = "juan.perez$timestamp@miempresa.com"; fkEmpresa = $empresa.oid; fkSucursal = $sucursal.oid; fkCargo = $cargo.oid }
$empleado = Invoke-RestMethod -Uri "http://localhost:8001/empleado/" -Method POST -Body ($body | ConvertTo-Json) -ContentType "application/json"
Write-Host "✓ Empleado OID: $($empleado.oid)"

# 6. Permiso
$timestamp = Get-Date -Format "HHmmss"
$body = @{ clave = "PERM$timestamp"; nombre = "Ver Dashboard"; permiso = "dashboard.view" }
$permiso = Invoke-RestMethod -Uri "http://localhost:8000/permiso/" -Method POST -Body ($body | ConvertTo-Json) -ContentType "application/json"
Write-Host "✓ Permiso OID: $($permiso.oid)"

# 7. Rol
$timestamp = Get-Date -Format "HHmmss"
$body = @{ nombre = "Administrador$timestamp" }
$rol = Invoke-RestMethod -Uri "http://localhost:8000/rol/" -Method POST -Body ($body | ConvertTo-Json) -ContentType "application/json"
Write-Host "✓ Rol OID: $($rol.oid)"

# 8. PermisoAsignado
$body = @{ fkPermiso = $permiso.oid; fkRol = $rol.oid; crear = $true; editar = $true; desactivar = $true; cancelar = $false }
$permisoAsignado = Invoke-RestMethod -Uri "http://localhost:8000/permiso_asignado/" -Method POST -Body ($body | ConvertTo-Json) -ContentType "application/json"
Write-Host "✓ PermisoAsignado OID: $($permisoAsignado.oid)"

# 9. Usuario
$timestamp = Get-Date -Format "HHmmss"
$jsonString = "{`"usuario`":`"jperez$timestamp`",`"contraseña`":`"Pass123`",`"fkSistema`":`"$($sistema.oid)`",`"fkEmpleado`":`"$($empleado.oid)`"}"
$bytes = [System.Text.Encoding]::UTF8.GetBytes($jsonString)
$usuario = Invoke-RestMethod -Uri "http://localhost:8000/usuario/" -Method POST -Body $bytes -ContentType "application/json; charset=utf-8"
Write-Host "✓ Usuario OID: $($usuario.oid)"

# 10. UsuarioRol
$body = @{ fkUsuario = $usuario.oid; fkRol = $rol.oid }
$usuarioRol = Invoke-RestMethod -Uri "http://localhost:8000/usuario_rol/" -Method POST -Body ($body | ConvertTo-Json) -ContentType "application/json"
Write-Host "✓ UsuarioRol OID: $($usuarioRol.oid)"

# Verificar Usuario Completo
Write-Host "`n=== Usuario Completo ===" -ForegroundColor Green
$usuarioCompleto = Invoke-RestMethod -Uri "http://localhost:8000/usuario/$($usuario.oid)" -Method GET
$usuarioCompleto | ConvertTo-Json -Depth 10

# 11. Login (Verificación)
Write-Host "`n=== Probando Login ===" -ForegroundColor Yellow
$jsonString = "{`"usuario`":`"jperez$timestamp`",`"contraseña`":`"Pass123`"}"
$bytes = [System.Text.Encoding]::UTF8.GetBytes($jsonString)
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method POST -Body $bytes -ContentType "application/json; charset=utf-8"
Write-Host "✓ Login exitoso!" -ForegroundColor Green
Write-Host "  Access Token: $($loginResponse.access_token.Substring(0,50))..." -ForegroundColor Cyan
Write-Host "  Usuario: $($loginResponse.usuario.usuario)" -ForegroundColor Cyan
```

---

## Notas Importantes

1. **Timestamps únicos:** Uso de `$timestamp` para evitar duplicados en campos únicos (clave, usuario, email, etc.)

2. **Codificación UTF-8:** El campo `contraseña` requiere codificación UTF-8 explícita debido a la ñ

3. **Prefijos de URLs:** 
   - Catalogues Service: `/sistema/`, `/empresa/`, `/sucursal/`
   - Branch Service: `/cargo/`, `/empleado/`
   - Auth Service: `/permiso/`, `/rol/`, `/permiso_asignado/`, `/usuario/`, `/usuario_rol/`

4. **Puertos:**
   - Auth Service: 8000
   - Branch Service: 8001
   - Catalogues Service: 8002

5. **Dependencias:** Seguir el orden de creación estricto para evitar errores de foreign keys

6. **Verificación:** Cada entidad puede verificarse mediante GET usando su OID: `http://localhost:{puerto}/{endpoint}/{oid}`

---

## 11. Login (Bonus)

**Servicio:** Auth Service (Puerto 8000)  
**Endpoint:** POST /auth/login  
**Dependencias:** Requiere usuario creado con contraseña

```powershell
$jsonString = "{`"usuario`":`"jperez161855`",`"contraseña`":`"Pass123`"}"
$bytes = [System.Text.Encoding]::UTF8.GetBytes($jsonString)
$response = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method POST -Body $bytes -ContentType "application/json; charset=utf-8"
Write-Host "Access Token: $($response.access_token)"
Write-Host "Refresh Token: $($response.refresh_token)"
Write-Host "Usuario: $($response.usuario.usuario)"
```

**Respuesta exitosa:**
- `access_token`: Token JWT para autenticación
- `refresh_token`: Token para renovar el access_token
- `usuario`: Objeto completo del usuario con todas sus relaciones

---

**Fecha de creación:** 19 de Marzo, 2026  
**Estado:** Probado y funcional ✓ (Incluye Login)
