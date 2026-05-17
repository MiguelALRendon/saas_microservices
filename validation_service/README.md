# Validation Service

Microservicio de validaciones y lógica de negocio.

## Propósito
Este servicio se encarga de:
- Validaciones de reglas de negocio
- Procesamiento de lógica sin persistencia
- Orquestación de validaciones entre servicios

## Características
- **Sin base de datos:** Este servicio no persiste datos
- **Stateless:** Todas las operaciones son sin estado
- **Validaciones:** Se enfoca en reglas de negocio y validaciones

## Instalación
```bash
pip install -r requirements.txt
```

## Configuración
Copiar `.env.example` a `.env` y configurar las variables de entorno.

## Dependencias
Este servicio puede consumir APIs de otros microservicios para realizar validaciones.
