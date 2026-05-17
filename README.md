# SaaS API - Microservices Architecture

Backend de la aplicación SaaS dividido en microservicios independientes.

## 🏗️ Arquitectura de Microservicios

Este proyecto está organizado en 6 microservicios independientes, cada uno con su propia base de datos:

### 1. 🔐 **Auth Service** (`auth_service/`)
- **Base de datos:** `auth_service_db`
- **Responsabilidad:** Autenticación, autorización y gestión de usuarios
- **Modelos:** Usuario, Rol, UsuarioRol, Permiso, PermisoAsignado

### 2. 📋 **Catalogues Service** (`catalogues_service/`)
- **Base de datos:** `catalogues_service_db`
- **Responsabilidad:** Catálogos maestros (empresas, sucursales, sistemas, productos)
- **Modelos:** Empresa, Sucursal, Sistema, Producto

### 3. 🏪 **Branch Service** (`branch_service/`)
- **Base de datos:** `branch_service_db`
- **Responsabilidad:** Gestión de turnos y cortes de caja
- **Modelos:** TurnoSucursal, CorteCaja

### 4. 📦 **Inventory Service** (`inventory_service/`)
- **Base de datos:** `inventory_service_db`
- **Responsabilidad:** Gestión de stock e inventarios
- **Modelos:** StockSucursal, ListaPrecios, InventarioLotes

### 5. 🚚 **Supplier Service** (`supplier_service/`)
- **Base de datos:** `supplier_service_db`
- **Responsabilidad:** Proveedores y sus relaciones
- **Modelos:** ProveedorEmpleado, ProveedorEmpresa, ProveedorMarca, ProveedorProducto

### 6. 💰 **Sales Service** (`sales_service/`)
- **Base de datos:** `sales_service_db`
- **Responsabilidad:** Gestión de ventas, entradas y traspasos de mercancía
- **Modelos:** Venta, VentaDetalle, EntradaMercancia, EntradaMercanciaDetalle, TraspasoMercancia, TraspasoMercanciaDetalle

---

## 🚀 Instalación y Configuración

Cada microservicio es independiente y debe configurarse por separado.

### Requisitos Generales
- Python 3.10+
- MySQL 8.0+

### Configuración por Microservicio

Para cada microservicio (auth_service, branch_service, inventory_service, supplier_service, sales_service):

1. **Crear entorno virtual:**
```bash
cd <nombre_servicio>
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno:**
```bash
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
```
Editar `.env` con la configuración de base de datos correspondiente.

4. **Crear base de datos MySQL:**
```sql
CREATE DATABASE <nombre_base_datos>;
```

5. **Inicializar migraciones:**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

---

## 📊 Bases de Datos

Crear las siguientes bases de datos en MySQL:
- `auth_service_db`
- `catalogues_service_db`
- `branch_service_db`
- `inventory_service_db`
- `supplier_service_db`
- `sales_service_db`

---

## 🔗 Comunicación entre Microservicios

Los microservicios están diseñados para comunicarse entre sí mediante APIs REST. Las foreign keys que referencian otras bases de datos se almacenan como strings (OIDs) sin constraints de base de datos.

---

## 📝 Notas de Desarrollo

- Cada servicio tiene su clase `Base` y `BaseContactoObject` independiente
- Los enums se duplican en cada servicio que los necesita
- No hay dependencias de código entre servicios
- Cada servicio puede desplegarse y escalar independientemente

## 📁 Estructura de Directorios

```
saas_api/
├── auth_service/
│   ├── app/
│   │   ├── models/
│   │   └── enums/
│   ├── config.py
│   ├── requirements.txt
│   └── .env.example
├── branch_service/
│   └── ...
├── inventory_service/
│   └── ...
├── supplier_service/
│   └── ...
└── sales_service/
    └── ...
```
