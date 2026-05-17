# Estándares de Desarrollo - Microservicios SaaS

Este documento define los estándares de código, estructura, configuración y mejores prácticas para todos los microservicios del proyecto SaaS.

---

## 📁 Estructura de Proyecto

Todos los microservicios deben seguir esta estructura:

```
{service_name}/
├── app/
│   ├── __init__.py              # Factory de aplicación Flask
│   ├── enums/
│   │   ├── __init__.py
│   │   └── base_object_estatus.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py              # BaseObject para herencia
│   │   ├── base_contacto.py     # (opcional) Para entidades con contacto
│   │   └── {entity}.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── {entity}_routes.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── base_schema.py
│   │   └── {entity}_schema.py
│   └── external_{service_name}/        # Referencias a microservicios externos
│       ├── __init__.py
│       └── {entity}_external.py        # Wrapper GET-only para microservicio externo
├── config.py                    # Configuración centralizada
├── run.py                       # Punto de entrada de la aplicación
├── requirements.txt             # Dependencias Python
├── .env.example                 # Plantilla de variables de entorno
└── README.md                    # Documentación del servicio
```

---

## 🗄️ Normalización de Base de Datos

### 1. BaseObject - Clase Base para Todos los Modelos

Todos los modelos deben heredar de `BaseObject`:

```python
import uuid
from datetime import datetime
from app import db
from app.enums import BaseObjectEstatus

class BaseObject(db.Model):
    __abstract__ = True
    
    oid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    creado_por = db.Column(db.String(36), nullable=True)
    editado_por = db.Column(db.String(36), nullable=True)
    estatus = db.Column(db.Enum(BaseObjectEstatus), nullable=False, default=BaseObjectEstatus.ACTIVO)
```

### 1.1. BaseContactoObject - Clase Base con Información de Contacto

Para entidades que requieren información de contacto (teléfono y email), usar `BaseContactoObject`:

```python
from app import db
from .base import BaseObject

class BaseContactoObject(BaseObject):
    __abstract__ = True
    
    telefono = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
```

**Uso:**
```python
class Empresa(BaseContactoObject):
    __tablename__ = 'empresa'
    
    clave = db.Column(db.String(50), nullable=False, unique=True, index=True)
    nombre = db.Column(db.String(200), nullable=False, index=True)
    # telefono y email ya están incluidos por herencia
```

**Campos obligatorios en todas las tablas:**
- `oid`: UUID como clave primaria (String 36)
- `createdAt`: Fecha de creación (DateTime, auto)
- `updatedAt`: Fecha de última actualización (DateTime, auto)
- `creado_por`: Usuario que creó el registro (String 36, nullable)
- `editado_por`: Usuario que editó el registro (String 36, nullable)
- `estatus`: Estado del registro (Enum: ACTIVO, INACTIVO, ELIMINADO)

### 2. Enums - Convención General

Todos los enums del proyecto siguen dos reglas obligatorias:

1. **Heredar de `(str, Enum)`** — el valor del enum es directamente un `str`, por lo que `jsonify()` lo serializa sin encoder personalizado. Un `enum.Enum` puro lanza `TypeError` al intentar serializar a JSON.
2. **Valores en UPPERCASE idénticos al nombre del miembro** — elimina la asimetría cognitiva de recordar que `ACTIVO` almacena `"Activo"`. Con `ACTIVO = "ACTIVO"` el nombre y el valor son idénticos, los errores de comparación por case desaparecen y el JSON devuelto es inequívocamente un código de API, no un label de presentación.

```python
# ✅ Correcto
from enum import Enum

class BaseObjectEstatus(str, Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    ELIMINADO = "ELIMINADO"

class UnidadMedida(str, Enum):
    GRAMO = "GRAMO"
    KILOGRAMO = "KILOGRAMO"
    LITRO = "LITRO"
    MILILITRO = "MILILITRO"
    PIEZA = "PIEZA"

# ❌ Incorrecto — plain enum.Enum no serializa a JSON
class BaseObjectEstatus(enum.Enum):
    ACTIVO = "Activo"   # ❌ valor distinto al nombre crea asimetría
```

**Reglas:**
- Siempre `from enum import Enum` (no `import enum`)
- Siempre `class MiEnum(str, Enum)`
- Nombre del miembro == valor (ambos UPPER_SNAKE_CASE)
- Nunca mezclar estilos de valor dentro del mismo enum

### 2.1. BaseObjectEstatus

```python
from enum import Enum

class BaseObjectEstatus(str, Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    ELIMINADO = "ELIMINADO"
```

**Convención:**
- Usar soft delete (marcar como ELIMINADO)
- Nunca eliminar físicamente registros
- Filtrar registros ELIMINADOS en todas las consultas

### 3. Nomenclatura de Tablas y Columnas

**Tablas:**
- Nombres en minúsculas
- Singular (ej: `empresa`, `producto`, `usuario`)
- Snake_case para nombres compuestos (ej: `usuario_rol`)

**Columnas:**
- camelCase para campos propios (ej: `createdAt`, `updatedAt`)
- Snake_case para Foreign Keys con prefijo `fk` (ej: `fkEmpresa`, `fkProducto`)
- Campos de auditoría: `creado_por`, `editado_por` (snake_case)

**Índices:**
- Agregar índices a columnas de búsqueda frecuente
- Claves únicas donde sea necesario (ej: `clave`, `email`)

```python
class Producto(BaseObject):
    __tablename__ = 'producto'
    
    clave = db.Column(db.String(50), nullable=False, unique=True, index=True)
    nombre = db.Column(db.String(200), nullable=False, index=True)
    fkProveedorMarca = db.Column(db.String(36), nullable=True, index=True)
```

---

## 🐍 Estándares de Código Python

### 1. Modelos (models/)

```python
from app import db
from app.models.base import BaseObject

class Empresa(BaseObject):
    __tablename__ = 'empresa'
    
    # Campos específicos
    clave = db.Column(db.String(50), nullable=False, unique=True, index=True)
    nombre = db.Column(db.String(200), nullable=False, index=True)
    
    # Relaciones
    sucursales = db.relationship('Sucursal', back_populates='empresa', lazy='dynamic')
    
    def __repr__(self):
        return f'<Empresa {self.nombre}>'
```

**Reglas:**
- Heredar siempre de `BaseObject`
- Definir `__tablename__` explícitamente
- Agregar `__repr__` para debugging
- Usar `lazy='dynamic'` en relaciones de uno-a-muchos
- Documentar relaciones complejas

### 2. Schemas (schemas/)

```python
from .base_schema import BaseSchema

class EmpresaSchema(BaseSchema):
    """Schema para serialización y validación de Empresa"""
    
    @staticmethod
    def serialize(empresa):
        """Serializa una empresa a diccionario"""
        data = BaseSchema.serialize_base(empresa)
        data.update({
            'clave': empresa.clave,
            'nombre': empresa.nombre,
            'folio': empresa.folio
        })
        return data
    
    @staticmethod
    def serialize_list(empresas):
        """Serializa una lista de empresas"""
        return [EmpresaSchema.serialize(empresa) for empresa in empresas]
    
    @staticmethod
    def validate_create(data):
        """Valida datos para crear una empresa"""
        errors = []
        
        if not data.get('clave'):
            errors.append('clave es requerida')
        if not data.get('nombre'):
            errors.append('nombre es requerido')
        
        return errors
    
    @staticmethod
    def validate_update(data):
        """Valida datos para actualizar una empresa"""
        # Para update, los campos no son obligatorios
        return []
```

**BaseSchema compartido:**

```python
class BaseSchema:
    """Schema base con métodos comunes"""
    
    @staticmethod
    def serialize_base(obj):
        """Serializa campos base de BaseObject"""
        return {
            'oid': obj.oid,
            'createdAt': obj.createdAt.isoformat() if obj.createdAt else None,
            'updatedAt': obj.updatedAt.isoformat() if obj.updatedAt else None,
            'creado_por': obj.creado_por,
            'editado_por': obj.editado_por,
            'estatus': obj.estatus.value if obj.estatus else None
        }
```

**Reglas:**
- Métodos estáticos (no instanciar schemas)
- Siempre incluir: `serialize`, `serialize_list`, `validate_create`, `validate_update`
- Heredar de `BaseSchema` y usar `serialize_base`
- Retornar lista de errores (strings) en validación

### 2.1. Resolución de Referencias FK en Serialización

Cuando un modelo tiene columnas FK (`fk*`) que apuntan a objetos de otras tablas, los schemas **deben** resolver y serializar esos objetos completos en la respuesta, no solo exponer el ID.

**Reglas:**
- **FK mismo microservicio**: utilizar el `relationship` de SQLAlchemy o hacer una consulta directa (la columna FK ya está indexada). Exponer el objeto serializado completo.
- **FK microservicio externo**: llamar al módulo `external_` correspondiente usando `get_by_oid`.
- Nombrar la propiedad resuelta sin el prefijo `fk` y en minúsculas: `fkEmpresa` → `empresa`, `fkRol` → `rol`.
- Si la FK es `nullable` y no tiene valor, devolver `null` para esa propiedad.
- Las columnas FK originales (`fkEmpresa`, `fkRol`) **también** se siguen incluyendo para compatibilidad.

**Ejemplo - FK mismo microservicio:**
```python
from app.schemas.empresa_schema import EmpresaSchema

@staticmethod
def serialize(sucursal):
    data = BaseSchema.serialize_base(sucursal)
    data.update({
        'clave': sucursal.clave,
        'nombre': sucursal.nombre,
        'fkEmpresa': sucursal.fkEmpresa,
        # Objeto FK resuelto del mismo microservicio (via relationship de SQLAlchemy)
        'empresa': EmpresaSchema.serialize(sucursal.empresa) if sucursal.empresa else None,
    })
    return data
```

**Ejemplo - FK microservicio externo:**
```python
from app.external_catalogues.empresa_external import EmpresaExternal

@staticmethod
def serialize(usuario):
    data = BaseSchema.serialize_base(usuario)
    data.update({
        'nombre': usuario.nombre,
        'fkEmpresa': usuario.fkEmpresa,
        # Objeto FK resuelto de otro microservicio via módulo external_
        'empresa': EmpresaExternal.get_by_oid(usuario.fkEmpresa) if usuario.fkEmpresa else None,
    })
    return data
```

### 2.2. Tablas Intermedias y Listas de Objetos Relacionados

Las tablas intermedias (junction tables) y cualquier entidad que maneje colecciones de referencias FK **deben** incluir los objetos reales resueltos en su serialización, nunca listas de IDs.

**Reglas:**
- Exponer listas de objetos completos, no listas de OIDs.
- Nombrar la propiedad en plural del objeto referenciado (ej: `roles`, `permisos`, `sucursales`).
- Si los objetos vienen de otro microservicio, utilizar `get_by_oid_list` del módulo `external_` para hacer una sola llamada eficiente con todos los OIDs en batch.
- Nunca devolver únicamente listas de IDs cuando existen objetos resolvibles.

**Ejemplo - tabla intermedia con objetos resueltos (mismo microservicio):**
```python
@staticmethod
def serialize(usuario_rol):
    data = BaseSchema.serialize_base(usuario_rol)
    data.update({
        'fkUsuario': usuario_rol.fkUsuario,
        'fkRol': usuario_rol.fkRol,
        # Objetos reales resueltos via relationships
        'usuario': UsuarioSchema.serialize(usuario_rol.usuario) if usuario_rol.usuario else None,
        'rol': RolSchema.serialize(usuario_rol.rol) if usuario_rol.rol else None,
    })
    return data
```

**Ejemplo - entidad con lista de referencias a microservicio externo (batch):**
```python
from app.external_catalogues.sucursal_external import SucursalExternal

@staticmethod
def serialize(usuario):
    data = BaseSchema.serialize_base(usuario)
    # Recolectar todos los OIDs y hacer una sola llamada batch
    oid_sucursales = [us.fkSucursal for us in usuario.usuario_sucursales if us.fkSucursal]
    sucursales = SucursalExternal.get_by_oid_list(oid_sucursales) if oid_sucursales else []
    data.update({
        'nombre': usuario.nombre,
        'sucursales': sucursales,  # Lista de objetos completos, no IDs
    })
    return data
```

### 3. Rutas (routes/)

Cada entidad debe tener estos endpoints estándar:

```python
from flask import Blueprint, request, jsonify
from app import db
from app.models.entity import Entity
from app.schemas.entity_schema import EntitySchema
from app.enums import BaseObjectEstatus
from datetime import datetime

entity_bp = Blueprint('entity', __name__, url_prefix='/entity')

# 1. GET /{entity}/<oid> - Obtener por OID
@entity_bp.route('/<string:oid>', methods=['GET'])
def get_entity(oid):
    """Obtiene una entidad por su OID"""
    try:
        entity = Entity.query.filter(
            Entity.oid == oid,
            Entity.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not entity:
            return jsonify({'errors': ['Entidad no encontrada']}), 404
        
        return jsonify(EntitySchema.serialize(entity)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500

# 2. GET /{entity}/ - Listar con paginación y filtros
@entity_bp.route('/', methods=['GET'])
def get_entities():
    """Obtiene listado de entidades con paginación y filtros"""
    try:
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Parámetros de filtrado
        clave = request.args.get('clave', type=str)
        nombre = request.args.get('nombre', type=str)
        
        # Query base - excluir eliminados
        query = Entity.query.filter(Entity.estatus != BaseObjectEstatus.ELIMINADO)
        
        # Aplicar filtros
        if clave:
            query = query.filter(Entity.clave.ilike(f'%{clave}%'))
        if nombre:
            query = query.filter(Entity.nombre.ilike(f'%{nombre}%'))
        
        # Paginación
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'data': EntitySchema.serialize_list(pagination.items),
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages
        }), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500

# 3. POST /{entity}/ - Crear una entidad
@entity_bp.route('/', methods=['POST'])
def create_entity():
    """Crea una nueva entidad"""
    try:
        data = request.get_json()
        
        # Validar datos
        errors = EntitySchema.validate_create(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Verificar unicidad si aplica
        if Entity.query.filter_by(clave=data['clave']).first():
            return jsonify({'errors': ['La clave ya existe']}), 400
        
        # Crear entidad
        entity = Entity(
            clave=data['clave'],
            nombre=data['nombre'],
            creado_por=data.get('creado_por'),
            estatus=BaseObjectEstatus.ACTIVO
        )
        
        db.session.add(entity)
        db.session.commit()
        
        return jsonify(EntitySchema.serialize(entity)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500

# 4. POST /{entity}/many - Crear múltiples entidades
@entity_bp.route('/many', methods=['POST'])
def create_many_entities():
    """Crea múltiples entidades"""
    try:
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de entidades']}), 400
        
        entities_created = []
        errors = []
        
        for idx, item in enumerate(data):
            # Validar datos
            validation_errors = EntitySchema.validate_create(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            
            # Verificar unicidad
            if Entity.query.filter_by(clave=item['clave']).first():
                errors.append({'index': idx, 'errors': ['La clave ya existe']})
                continue
            
            # Crear entidad
            entity = Entity(
                clave=item['clave'],
                nombre=item['nombre'],
                creado_por=item.get('creado_por'),
                estatus=BaseObjectEstatus.ACTIVO
            )
            
            db.session.add(entity)
            entities_created.append(entity)
        
        if entities_created:
            db.session.commit()
        
        response = {
            'created': len(entities_created),
            'data': EntitySchema.serialize_list(entities_created)
        }
        
        if errors:
            response['errors'] = errors
        
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500

# 5. PUT /{entity}/<oid> - Actualizar una entidad
@entity_bp.route('/<string:oid>', methods=['PUT'])
def update_entity(oid):
    """Actualiza una entidad"""
    try:
        entity = Entity.query.filter(
            Entity.oid == oid,
            Entity.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not entity:
            return jsonify({'errors': ['Entidad no encontrada']}), 404
        
        data = request.get_json()
        
        # Validar datos
        errors = EntitySchema.validate_update(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # Actualizar campos
        if 'clave' in data:
            # Verificar unicidad si se cambia la clave
            existing = Entity.query.filter(
                Entity.clave == data['clave'],
                Entity.oid != oid
            ).first()
            if existing:
                return jsonify({'errors': ['La clave ya existe']}), 400
            entity.clave = data['clave']
        
        if 'nombre' in data:
            entity.nombre = data['nombre']
        
        if 'editado_por' in data:
            entity.editado_por = data['editado_por']
        
        entity.updatedAt = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(EntitySchema.serialize(entity)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500

# 6. PUT /{entity}/many - Actualizar múltiples entidades
@entity_bp.route('/many', methods=['PUT'])
def update_many_entities():
    """Actualiza múltiples entidades"""
    try:
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({'errors': ['Se esperaba una lista de entidades']}), 400
        
        entities_updated = []
        errors = []
        
        for idx, item in enumerate(data):
            if 'oid' not in item:
                errors.append({'index': idx, 'errors': ['oid es requerido']})
                continue
            
            entity = Entity.query.filter(
                Entity.oid == item['oid'],
                Entity.estatus != BaseObjectEstatus.ELIMINADO
            ).first()
            
            if not entity:
                errors.append({'index': idx, 'errors': ['Entidad no encontrada']})
                continue
            
            # Validar datos
            validation_errors = EntitySchema.validate_update(item)
            if validation_errors:
                errors.append({'index': idx, 'errors': validation_errors})
                continue
            
            # Actualizar campos
            if 'nombre' in item:
                entity.nombre = item['nombre']
            
            if 'editado_por' in item:
                entity.editado_por = item['editado_por']
            
            entity.updatedAt = datetime.utcnow()
            entities_updated.append(entity)
        
        if entities_updated:
            db.session.commit()
        
        response = {
            'updated': len(entities_updated),
            'data': EntitySchema.serialize_list(entities_updated)
        }
        
        if errors:
            response['errors'] = errors
        
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500

# 7. DELETE /{entity}/<oid> - Eliminar (soft delete)
@entity_bp.route('/<string:oid>', methods=['DELETE'])
def delete_entity(oid):
    """Elimina (soft delete) una entidad"""
    try:
        entity = Entity.query.filter(
            Entity.oid == oid,
            Entity.estatus != BaseObjectEstatus.ELIMINADO
        ).first()
        
        if not entity:
            return jsonify({'errors': ['Entidad no encontrada']}), 404
        
        data = request.get_json()
        
        # Soft delete
        entity.estatus = BaseObjectEstatus.ELIMINADO
        entity.editado_por = data.get('editado_por')
        entity.updatedAt = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Entidad eliminada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 500

# 8. POST /{entity}/list - Obtener lista específica por OIDs
@entity_bp.route('/list', methods=['POST'])
def get_entity_list():
    """Obtiene una lista específica de entidades a partir de un arreglo de OIDs"""
    try:
        data = request.get_json()
        
        if not data or 'oid_list' not in data:
            return jsonify({'errors': ['oid_list es requerido']}), 400
        
        oid_list = data.get('oid_list', [])
        
        if not isinstance(oid_list, list):
            return jsonify({'errors': ['oid_list debe ser un arreglo']}), 400
        
        entities = Entity.query.filter(
            Entity.oid.in_(oid_list),
            Entity.estatus != BaseObjectEstatus.ELIMINADO
        ).all()
        
        return jsonify(EntitySchema.serialize_list(entities)), 200
    except Exception as e:
        return jsonify({'errors': [str(e)]}), 500
```

**Endpoints obligatorios:**
1. `GET /{entity}/<oid>` - Obtener por ID
2. `GET /{entity}/` - Listar con paginación y filtros
3. `POST /{entity}/` - Crear uno
4. `POST /{entity}/many` - Crear múltiples
5. `PUT /{entity}/<oid>` - Actualizar uno
6. `PUT /{entity}/many` - Actualizar múltiples
7. `DELETE /{entity}/<oid>` - Eliminación lógica
8. `POST /{entity}/list` - Obtener lista específica por OIDs

**Reglas de rutas:**
- Siempre usar Blueprint con prefijo de entidad
- Manejar errores con try/except
- Rollback en caso de error
- Siempre excluir ELIMINADOS en consultas GET
- Validar datos antes de crear/actualizar
- Retornar códigos HTTP apropiados (200, 201, 400, 404, 500)
- Incluir `editado_por` en actualizaciones y eliminaciones
- **TODAS las respuestas de error deben usar `{"errors": ["mensaje"]}` (array), nunca `{"error": "mensaje"}` (singular)**

### 4. Factory de Aplicación (app/__init__.py)

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    # Importar modelos para que SQLAlchemy los registre
    with app.app_context():
        from app import models
    
    # Registrar blueprints
    from app.routes import entity1_bp, entity2_bp
    app.register_blueprint(entity1_bp)
    app.register_blueprint(entity2_bp)
    
    return app
```

### 5. Punto de Entrada (run.py)

```python
from app import create_app, db
from config import Config

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Crear tablas si no existen
        db.create_all()
    
    # Usar variables de entorno para configuración del servidor
    app.run(
        debug=Config.DEBUG,
        host=Config.HOST,
        port=Config.PORT
    )
```

---

## 🌐 Módulos Externos (external_{service_name}/)

Cuando un microservicio necesita consumir datos de otro microservicio (por ejemplo, `auth_service` consulta `Empresa` y `Sucursal` del `catalogues_service`), se crean módulos proxy dentro de una carpeta `external_{service_name}/` dentro de `app/`.

### Propósito

- Centralizar todas las llamadas HTTP a microservicios externos en un solo lugar.
- Proveer una interfaz limpia y reutilizable para que los schemas resuelvan FKs externas.
- Solo implementar operaciones de **lectura** (GET). Las operaciones de escritura son **deuda técnica**.

### Estructura

```
app/
└── external_{service_name}/
    ├── __init__.py
    └── {entity}_external.py
```

Se crea una carpeta `external_` por cada microservicio externo referenciado, y un archivo por cada entidad que se consulta:

```
app/
├── external_catalogues/
│   ├── __init__.py
│   ├── empresa_external.py
│   └── sucursal_external.py
└── external_auth/
    ├── __init__.py
    └── usuario_external.py
```

### Implementación

Cada archivo `{entity}_external.py` contiene una clase con tres métodos estáticos de solo lectura:

```python
import requests
from config import Config

class EmpresaExternal:
    """Wrapper GET-only para Empresa del catalogues_service.
    
    TODO: Deuda técnica - implementar create/update cuando se configure
          autenticación entre servicios (service tokens / API keys).
    """
    
    BASE_URL = Config.CATALOGUES_SERVICE_URL
    
    @staticmethod
    def get_by_oid(oid: str) -> dict | None:
        """Obtiene una empresa por su OID"""
        try:
            response = requests.get(f'{EmpresaExternal.BASE_URL}/empresa/{oid}')
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
    
    @staticmethod
    def get_list(page: int = 1, per_page: int = 10, **filters) -> dict:
        """Obtiene el listado paginado de empresas"""
        try:
            params = {'page': page, 'per_page': per_page, **filters}
            response = requests.get(f'{EmpresaExternal.BASE_URL}/empresa/', params=params)
            if response.status_code == 200:
                return response.json()
            return {'data': [], 'total': 0, 'page': page, 'per_page': per_page, 'pages': 0}
        except Exception:
            return {'data': [], 'total': 0, 'page': page, 'per_page': per_page, 'pages': 0}
    
    @staticmethod
    def get_by_oid_list(oid_list: list) -> list:
        """Obtiene una lista específica de empresas por sus OIDs"""
        try:
            response = requests.post(
                f'{EmpresaExternal.BASE_URL}/empresa/list',
                json={'oid_list': oid_list}
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception:
            return []
    
    # TODO: Deuda técnica - habilitar cuando se configure autenticación entre servicios
    # @staticmethod
    # def create(data: dict) -> dict | None: ...
    #
    # @staticmethod
    # def update(oid: str, data: dict) -> dict | None: ...
```

### Reglas

- **Solo lectura obligatorio**: los módulos `external_` solo implementan `get_by_oid`, `get_list` y `get_by_oid_list`.
- **POST y PUT son deuda técnica**: incluir el esqueleto de esos métodos comentado con `# TODO: Deuda técnica`.
- **Fallos silenciosos**: en caso de error de red o respuesta no 200, retornar `None` (objetos únicos) o `[]` / dict vacío (listas) — el microservicio no debe caerse por dependencias externas.
- **Un archivo por entidad externa**: si se necesitan `Empresa` y `Sucursal` del mismo servicio, crear `empresa_external.py` y `sucursal_external.py` por separado.
- **Usar `Config`** para las URLs base, nunca hardcodear direcciones.
- Agregar `requests` a `requirements.txt` si no está ya presente.

### Dependencia adicional

Agregar al `requirements.txt` del microservicio que use módulos `external_`:

```txt
requests==2.32.3
```

---

## ⚙️ Configuración (config.py)

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'dev-jwt-secret-key'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:@localhost:3306/microservices_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Server Configuration
    HOST = os.environ.get('HOST') or '0.0.0.0'
    PORT = int(os.environ.get('PORT') or 8000)
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')
    BASE_URL = os.environ.get('BASE_URL') or f'http://localhost:{os.environ.get("PORT", 8000)}'
    
    # Microservices URLs
    AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL') or 'http://localhost:8000'
    CATALOGUES_SERVICE_URL = os.environ.get('CATALOGUES_SERVICE_URL') or 'http://localhost:8002'
    BRANCH_SERVICE_URL = os.environ.get('BRANCH_SERVICE_URL') or 'http://localhost:8001'
    INVENTORY_SERVICE_URL = os.environ.get('INVENTORY_SERVICE_URL') or 'http://localhost:8003'
    SALES_SERVICE_URL = os.environ.get('SALES_SERVICE_URL') or 'http://localhost:8004'
    SUPPLIER_SERVICE_URL = os.environ.get('SUPPLIER_SERVICE_URL') or 'http://localhost:8005'
    VALIDATION_SERVICE_URL = os.environ.get('VALIDATION_SERVICE_URL') or 'http://localhost:8006'

    # Continental Microservices URLs
    CONTINENTAL_CONTENT_URL = os.environ.get('CONTINENTAL_CONTENT_URL') or 'http://localhost:8101'
    CONTINENTAL_MEDIA_URL = os.environ.get('CONTINENTAL_MEDIA_URL') or 'http://localhost:8102'
    CONTINENTAL_UTILITIES_URL = os.environ.get('CONTINENTAL_UTILITIES_URL') or 'http://localhost:8103'
```

**Reglas:**
- Siempre proporcionar valores por defecto
- Usar `load_dotenv()` al inicio
- Agrupar configuraciones por tipo
- PORT debe ser configurable
- Incluir URLs de todos los microservicios

---

## 🔐 Variables de Entorno (.env.example)

```bash
# Application Settings
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database Configuration
DATABASE_URL=mysql+pymysql://root:@localhost:3306/microservices_db

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False
BASE_URL=http://localhost:8000

# Microservices URLs
AUTH_SERVICE_URL=http://localhost:8000
CATALOGUES_SERVICE_URL=http://localhost:8002
BRANCH_SERVICE_URL=http://localhost:8001
INVENTORY_SERVICE_URL=http://localhost:8003
SALES_SERVICE_URL=http://localhost:8004
SUPPLIER_SERVICE_URL=http://localhost:8005
VALIDATION_SERVICE_URL=http://localhost:8006

# Continental Microservices URLs
CONTINENTAL_CONTENT_URL=http://localhost:8101
CONTINENTAL_MEDIA_URL=http://localhost:8102
CONTINENTAL_UTILITIES_URL=http://localhost:8103

# Allowed Apis
CONTINENTAL_API_URL=http://localhost:8200
```

**Puertos asignados:**
- auth_service: 8000
- branch_service: 8001
- catalogues_service: 8002
- inventory_service: 8003
- sales_service: 8004
- supplier_service: 8005
- validation_service: 8006
- continental_content: 8101
- continental_media: 8102
- continental_utilities: 8103
- api_gateway: 8200

**Reglas:**
- Incluir comentarios descriptivos
- Agrupar por sección
- Valores de ejemplo, nunca valores reales
- Incluir todos los microservicios
- Actualizar al agregar nuevas variables

---

## � Seguridad entre Microservicios (Trusted Service Middleware)

Todos los microservicios **deben** rechazar cualquier petición que no provenga de una fuente autorizada (otro microservicio o una API permitida). El mecanismo es un **token secreto compartido** enviado en el header `X-Internal-Service-Secret` en cada petición inter-servicio.

> **¿Por qué no CORS?** CORS es una política de seguridad del *navegador*. Estos servicios no son consumidos directamente desde el navegador, sino entre servidores. La validación debe hacerse en el servidor, verificando quién está haciendo la llamada.

---

### 1. Variable de Entorno

Agregar a `.env` y `.env.example` de cada microservicio:

```bash
# Internal Service Security
INTERNAL_SERVICE_SECRET=cambia-este-secreto-por-uno-seguro
```

> **Regla:** Todos los microservicios y APIs autorizadas deben compartir el **mismo valor** de `INTERNAL_SERVICE_SECRET`. Generar con `python -c "import secrets; print(secrets.token_hex(32))"`.

---

### 2. Configuración (config.py)

Agregar la variable en la clase `Config`:

```python
class Config:
    # ... resto de configuración ...

    # Internal Service Security
    INTERNAL_SERVICE_SECRET = os.environ.get('INTERNAL_SERVICE_SECRET') or 'dev-internal-secret'
```

---

### 3. Middleware (app/middleware/trusted_service.py)

Crear el archivo `app/middleware/trusted_service.py`:

```python
import secrets
from flask import request, jsonify, current_app


class TrustedServiceMiddleware:
    """
    Middleware que valida que toda petición entrante proviene de un microservicio
    o API autorizada mediante el header X-Internal-Service-Secret.

    Bloquea con 403 cualquier petición que no incluya el secreto correcto.
    """

    HEADER_NAME = 'X-Internal-Service-Secret'

    @staticmethod
    def validate():
        """
        Verifica el header de autenticación inter-servicio.
        Retorna (dict_error, status_code) si hay error, o (None, None) si es válido.
        Usar secrets.compare_digest para evitar timing attacks.
        """
        token = request.headers.get(TrustedServiceMiddleware.HEADER_NAME, '')
        expected = current_app.config.get('INTERNAL_SERVICE_SECRET', '')

        if not token or not secrets.compare_digest(token, expected):
            return {'errors': ['Acceso no autorizado']}, 403

        return None, None

    @staticmethod
    def register(app):
        """
        Registra el middleware como before_request en la aplicación Flask.
        Llamar desde create_app() después de inicializar extensiones.
        """
        @app.before_request
        def check_internal_secret():
            error, status = TrustedServiceMiddleware.validate()
            if error:
                return jsonify(error), status
```

**Crear también `app/middleware/__init__.py`** (si no existe):

```python
from .trusted_service import TrustedServiceMiddleware

__all__ = ['TrustedServiceMiddleware']
```

---

### 4. Registro en la Fábrica de Aplicación (app/__init__.py)

Registrar el middleware **después** de inicializar las extensiones:

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from app.middleware import TrustedServiceMiddleware

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Registrar middleware de seguridad inter-servicio
    TrustedServiceMiddleware.register(app)

    # Importar modelos para que SQLAlchemy los registre
    with app.app_context():
        from app import models

    # Registrar blueprints
    from app.routes import entity1_bp, entity2_bp
    app.register_blueprint(entity1_bp)
    app.register_blueprint(entity2_bp)

    return app
```

---

### 5. Header en Módulos Externos (external_/)

Todos los módulos `external_` **deben** incluir el header `X-Internal-Service-Secret` en cada petición HTTP saliente. Actualizar la clase base de cada `{entity}_external.py`:

```python
import requests
from config import Config


class EmpresaExternal:
    BASE_URL = Config.CATALOGUES_SERVICE_URL

    @staticmethod
    def _headers() -> dict:
        """Cabeceras de autenticación inter-servicio."""
        return {'X-Internal-Service-Secret': Config.INTERNAL_SERVICE_SECRET}

    @staticmethod
    def get_by_oid(oid: str) -> dict | None:
        try:
            response = requests.get(
                f'{EmpresaExternal.BASE_URL}/empresa/{oid}',
                headers=EmpresaExternal._headers()
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None

    @staticmethod
    def get_list(page: int = 1, per_page: int = 10, **filters) -> dict:
        try:
            params = {'page': page, 'per_page': per_page, **filters}
            response = requests.get(
                f'{EmpresaExternal.BASE_URL}/empresa/',
                params=params,
                headers=EmpresaExternal._headers()
            )
            if response.status_code == 200:
                return response.json()
            return {'data': [], 'total': 0, 'page': page, 'per_page': per_page, 'pages': 0}
        except Exception:
            return {'data': [], 'total': 0, 'page': page, 'per_page': per_page, 'pages': 0}

    @staticmethod
    def get_by_oid_list(oid_list: list) -> list:
        try:
            response = requests.post(
                f'{EmpresaExternal.BASE_URL}/empresa/list',
                json={'oid_list': oid_list},
                headers=EmpresaExternal._headers()
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception:
            return []
```

> **Regla:** El método `_headers()` es privado por convención (`_` prefijo). Todos los métodos `get_*` deben pasarlo en cada llamada `requests.get` / `requests.post`.

---

### 6. Resumen del Flujo

```
[Cliente externo sin secreto]  ──→  Microservicio  ──→  403 Acceso no autorizado
[Microservicio A con secreto]  ──→  Microservicio B ──→  200 OK
[API Gateway con secreto]      ──→  Microservicio  ──→  200 OK
[CONTINENTAL_API con secreto]  ──→  Microservicio  ──→  200 OK
```

---

## �📦 Dependencias (requirements.txt)

```txt
Flask==3.1.2
Flask-SQLAlchemy==3.1.1
python-dotenv==1.2.1
psycopg2-binary==2.9.11
Flask-Migrate==4.1.0
PyMySQL==1.1.0
```

**Dependencias estándar obligatorias:**
- Flask
- Flask-SQLAlchemy
- python-dotenv
- Driver de BD (psycopg2-binary o PyMySQL)
- Flask-Migrate (opcional pero recomendado)

---

## 📖 Respuestas de API Estándar

### Respuesta Exitosa - Objeto Único (200)
```json
{
  "oid": "123e4567-e89b-12d3-a456-426614174000",
  "createdAt": "2024-01-01T00:00:00",
  "updatedAt": "2024-01-01T00:00:00",
  "creado_por": "user-123",
  "editado_por": null,
  "estatus": "Activo",
  "clave": "PROD-001",
  "nombre": "Producto Ejemplo"
}
```

### Respuesta Exitosa - Lista Paginada (200)
```json
{
  "data": [...],
  "total": 100,
  "page": 1,
  "per_page": 10,
  "pages": 10
}
```

### Respuesta de Creación (201)
```json
{
  "oid": "123e4567-e89b-12d3-a456-426614174000",
  ...campos del objeto
}
```

### Respuesta de Creación Múltiple (201)
```json
{
  "created": 5,
  "data": [...],
  "errors": [
    {
      "index": 2,
      "errors": ["La clave ya existe"]
    }
  ]
}
```

### Respuesta de Error - Validación (400)
```json
{
  "errors": [
    "clave es requerida",
    "nombre es requerido"
  ]
}
```

### Respuesta de Error - No Encontrado (404)
```json
{
  "errors": [
    "Entidad no encontrada"
  ]
}
```

### Respuesta de Error - Conflicto (400)
```json
{
  "errors": [
    "La clave ya existe"
  ]
}
```

### Respuesta de Error - Servidor (500)
```json
{
  "errors": [
    "Mensaje de error descriptivo"
  ]
}
```

**⚠️ IMPORTANTE:** TODAS las respuestas de error deben usar el formato `{"errors": ["mensaje"]}`, incluso si es un solo error. Nunca usar `{"error": "mensaje"}` en singular.

---

## 🎨 Convenciones de Nomenclatura

### Python
- **Archivos**: snake_case (ej: `empresa_routes.py`)
- **Clases**: PascalCase (ej: `EmpresaSchema`)
- **Funciones/métodos**: snake_case (ej: `get_empresa()`)
- **Variables**: snake_case
- **Constantes**: UPPER_SNAKE_CASE
- **Blueprints**: entity_bp (ej: `empresa_bp`)

### Base de Datos
- **Tablas**: singular, lowercase (ej: `empresa`, `producto`)
- **Columnas propias**: camelCase (ej: `createdAt`, `urlLogo`)
- **Columnas de auditoría**: snake_case (ej: `creado_por`)
- **Foreign Keys**: camelCase con prefijo `fk` (ej: `fkEmpresa`)

### API
- **Endpoints**: lowercase, plural para listar (ej: `/empresa/`, `/productos/`)
- **Parámetros query**: snake_case
- **JSON keys**: camelCase para campos, snake_case para auditoría

---

## ✅ Checklist de Implementación

**📋 IMPORTANTE:** Al crear un nuevo microservicio:
1. Copiar este documento a la carpeta del microservicio para referencia
2. Limpiar todos los checkboxes a continuación
3. Marcar cada item conforme se complete la implementación
4. Mantener actualizado durante el desarrollo

Al crear un nuevo microservicio, verificar:

### Estructura
- [ ] Estructura de carpetas completa (app/, models/, routes/, schemas/, enums/)
- [ ] `__init__.py` en cada carpeta
- [ ] Carpetas `external_{service_name}/` creadas por cada microservicio externo referenciado

### Modelos
- [ ] Heredan de BaseObject
- [ ] Tienen `__tablename__` definido
- [ ] Tienen `__repr__` implementado
- [ ] Índices en campos de búsqueda
- [ ] Relaciones definidas correctamente

### Schemas
- [ ] Heredan de BaseSchema
- [ ] Implementan `serialize()`
- [ ] Implementan `serialize_list()`
- [ ] Implementan `validate_create()`
- [ ] Implementan `validate_update()`
- [ ] FKs al mismo microservicio resueltas como objetos completos (via relationships)
- [ ] FKs a microservicios externos resueltas via módulo `external_`
- [ ] Tablas intermedias devuelven objetos reales (no listas de IDs)

### Rutas
- [ ] 8 endpoints estándar implementados (incluye `POST /list`)
- [ ] Blueprint registrado en `app/__init__.py`
- [ ] Manejo de errores con try/except
- [ ] Rollback en caso de error
- [ ] Filtran registros ELIMINADOS
- [ ] Validación de datos

### Módulos Externos (external_)
- [ ] Carpeta `external_{service_name}/` creada por cada servicio externo referenciado
- [ ] `__init__.py` en cada carpeta `external_`
- [ ] Clase wrapper con métodos: `get_by_oid`, `get_list`, `get_by_oid_list`
- [ ] POST y PUT comentados como deuda técnica (`# TODO`)
- [ ] Método `_headers()` incluido en cada clase externa (envía `X-Internal-Service-Secret`)
- [ ] Todos los llamados `requests.get` / `requests.post` incluyen `headers=_headers()`
- [ ] `requests` agregado a `requirements.txt`

### Seguridad inter-servicio
- [ ] `INTERNAL_SERVICE_SECRET` en `.env` y `.env.example`
- [ ] `INTERNAL_SERVICE_SECRET` en `config.py`
- [ ] `app/middleware/trusted_service.py` creado
- [ ] `app/middleware/__init__.py` exporta `TrustedServiceMiddleware`
- [ ] `TrustedServiceMiddleware.register(app)` llamado en `create_app()`

### Configuración
- [ ] `config.py` con todas las secciones
- [ ] `.env.example` actualizado
- [ ] `requirements.txt` con dependencias correctas
- [ ] `run.py` con factory pattern

### Documentación
- [ ] README.md con instalación y uso
- [ ] Documentación de endpoints
- [ ] Ejemplos de API (opcional)

---

## 🔄 Proceso de Desarrollo

1. **Diseñar modelo de datos**
   - Definir entidades
   - Relaciones
   - Campos únicos e índices

2. **Implementar modelos**
   - Crear clases en `models/`
   - Heredar de BaseObject
   - Definir relaciones

3. **Crear módulos externos (si aplica)**
   - Identificar columnas FK que apuntan a otros microservicios
   - Crear carpeta `external_{service_name}/` por cada servicio externo referenciado
   - Implementar clase wrapper con `get_by_oid`, `get_list`, `get_by_oid_list`
   - Dejar POST/PUT comentados como deuda técnica
   - Agregar `requests` a `requirements.txt`

4. **Crear schemas**
   - Implementar serialización
   - Resolver FKs al mismo microservicio via relationships de SQLAlchemy
   - Resolver FKs externas via módulos `external_` (llamadas batch con `get_by_oid_list`)
   - Serializar objetos completos en tablas intermedias (no IDs)
   - Implementar validación

5. **Desarrollar rutas**
   - Crear Blueprint
   - Implementar 8 endpoints estándar (incluye `POST /list`)
   - Manejar errores

6. **Registrar Blueprint y Middleware**
   - Importar en `app/__init__.py`
   - Registrar con `register_blueprint()`
   - Llamar `TrustedServiceMiddleware.register(app)` en `create_app()`

7. **Configurar**
   - Actualizar `config.py` (incluir `INTERNAL_SERVICE_SECRET`)
   - Actualizar `.env.example` (incluir `INTERNAL_SERVICE_SECRET`)
   - Verificar puerto

8. **Documentar**
   - README.md
   - Ejemplos de uso

9. **Probar**
   - Crear tablas (`db.create_all()`)
   - Probar endpoints
   - Verificar respuestas

---

## 🚀 Ejemplo de Referencia

El microservicio **catalogues_service** es el ejemplo de referencia completo que implementa todos estos estándares correctamente.

Características del servicio de referencia:
- ✅ 4 entidades (Empresa, Producto, Sistema, Sucursal)
- ✅ Todos los endpoints implementados (7 por entidad)
- ✅ Documentación completa (README.md + API_EXAMPLES.md)
- ✅ Schemas con validación
- ✅ Manejo de errores robusto
- ✅ Configuración completa
- ✅ Paginación y filtros en listados

---

## 📚 Referencias

- **Flask**: https://flask.palletsprojects.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Flask-SQLAlchemy**: https://flask-sqlalchemy.palletsprojects.com/

---

**Última actualización:** Marzo 2026

Este documento debe actualizarse cuando se agreguen nuevos patrones o mejores prácticas al proyecto.
