# Sales Service

Microservicio de gestión de ventas, entradas y traspasos de mercancía.

## Modelos incluidos:
- Venta
- VentaDetalle
- EntradaMercancia
- EntradaMercanciaDetalle
- TraspasoMercancia
- TraspasoMercanciaDetalle

## Base de datos
- Base de datos: `sales_service_db`
- Tablas compartidas: `Base`
- Enums: `Pago`, `TipoCosto`, `TipoTraspaso`

## Instalación
```bash
pip install -r requirements.txt
```

## Configuración
Copiar `.env.example` a `.env` y configurar las variables de entorno.
