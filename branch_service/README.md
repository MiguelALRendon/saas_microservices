# Branch Service

Microservicio de gestión de sucursales: cargos, empleados, turnos y cortes de caja.

**Puerto:** `8001`

---

## Entidades

| Modelo | Tabla | Descripción |
|---|---|---|
| `Cargo` | `cargo` | Puestos de trabajo disponibles |
| `Empleado` | `empleado` | Empleados con datos personales y contacto |
| `TurnoSucursal` | `turno_sucursal` | Turnos laborales por sucursal |
| `CorteCaja` | `corte_caja` | Cortes de caja al cierre de turno |

---

## Instalación

```bash
pip install -r requirements.txt
```

## Configuración

```bash
cp .env.example .env
# Editar .env con los valores correctos
```

## Levantar el servicio

```bash
python run.py
```

---

## Endpoints

Todos los endpoints siguen el patrón estándar de 8 rutas por entidad.

### Cargo — `/cargo`

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/cargo/<oid>` | Obtener cargo por OID |
| GET | `/cargo/` | Listar cargos (paginado, filtros: `clave`, `nombre`) |
| POST | `/cargo/` | Crear cargo |
| POST | `/cargo/many` | Crear múltiples cargos |
| PUT | `/cargo/<oid>` | Actualizar cargo |
| PUT | `/cargo/many` | Actualizar múltiples cargos |
| DELETE | `/cargo/<oid>` | Eliminar cargo (soft delete) |
| POST | `/cargo/list` | Obtener lista por OIDs |

### Empleado — `/empleado`

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/empleado/<oid>` | Obtener empleado por OID |
| GET | `/empleado/` | Listar empleados (paginado, filtros: `nombres`, `apellido_paterno`, `fkEmpresa`, `fkSucursal`, `fkCargo`) |
| POST | `/empleado/` | Crear empleado |
| POST | `/empleado/many` | Crear múltiples empleados |
| PUT | `/empleado/<oid>` | Actualizar empleado |
| PUT | `/empleado/many` | Actualizar múltiples empleados |
| DELETE | `/empleado/<oid>` | Eliminar empleado (soft delete) |
| POST | `/empleado/list` | Obtener lista por OIDs |

### TurnoSucursal — `/turno_sucursal`

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/turno_sucursal/<oid>` | Obtener turno por OID |
| GET | `/turno_sucursal/` | Listar turnos (paginado, filtros: `nombre`, `fkEmpresa`, `fkSucursal`) |
| POST | `/turno_sucursal/` | Crear turno |
| POST | `/turno_sucursal/many` | Crear múltiples turnos |
| PUT | `/turno_sucursal/<oid>` | Actualizar turno |
| PUT | `/turno_sucursal/many` | Actualizar múltiples turnos |
| DELETE | `/turno_sucursal/<oid>` | Eliminar turno (soft delete) |
| POST | `/turno_sucursal/list` | Obtener lista por OIDs |

### CorteCaja — `/corte_caja`

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/corte_caja/<oid>` | Obtener corte por OID |
| GET | `/corte_caja/` | Listar cortes (paginado, filtros: `fkEmpresa`, `fkSucursal`, `fkUsuario`, `fkTurno`, `fecha_inicio`, `fecha_fin`) |
| POST | `/corte_caja/` | Crear corte |
| POST | `/corte_caja/many` | Crear múltiples cortes |
| PUT | `/corte_caja/<oid>` | Actualizar corte |
| PUT | `/corte_caja/many` | Actualizar múltiples cortes |
| DELETE | `/corte_caja/<oid>` | Eliminar corte (soft delete) |
| POST | `/corte_caja/list` | Obtener lista por OIDs |

---

## Dependencias externas

| Servicio | Módulo | Entidades consumidas |
|---|---|---|
| `catalogues_service` | `external_catalogues` | `Empresa`, `Sucursal`, `Sistema` |
| `auth_service` | `external_auth` | `Usuario` |

---

## Estructura del proyecto

```
branch_service/
├── app/
│   ├── __init__.py
│   ├── enums/
│   │   ├── __init__.py
│   │   └── base_object_estatus.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── base_contacto.py
│   │   ├── cargo.py
│   │   ├── empleado.py
│   │   ├── turno_sucursal.py
│   │   └── corte_caja.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── cargo_routes.py
│   │   ├── empleado_routes.py
│   │   ├── turno_sucursal_routes.py
│   │   └── corte_caja_routes.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── base_schema.py
│   │   ├── cargo_schema.py
│   │   ├── empleado_schema.py
│   │   ├── turno_sucursal_schema.py
│   │   └── corte_caja_schema.py
│   ├── external_catalogues/
│   │   ├── __init__.py
│   │   ├── empresa_external.py
│   │   ├── sucursal_external.py
│   │   └── sistema_external.py
│   └── external_auth/
│       ├── __init__.py
│       └── usuario_external.py
├── config.py
├── run.py
├── requirements.txt
├── .env.example
└── README.md
```

