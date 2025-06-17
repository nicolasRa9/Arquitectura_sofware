# Sistema WMS (Warehouse Management System) - Arquitectura SOA

Este proyecto implementa un sistema de gestión de almacén basado en arquitectura de servicios (SOA) con los siguientes componentes:

## 🏗️ Arquitectura del Sistema

### Servicios Implementados

| Servicio Lógico | Nombre del Servicio | RF Cubiertos | Datos que Maneja |
|----------------|-------------------|-------------|-----------------|
| Productos | `product_service` | RF-1 | Producto |
| Ubicaciones | `location_service` | RF-2 | Ubicacion, Estante, Zona |
| Optimización | `optimization_service` | RF-3, RF-4 | Lee Producto + Ubicacion y escribe sugerencias |
| Movimientos | `movement_service` | RF-5, RF-12 | Movimiento, Almacenamiento |
| Visualización | `visualization_service` | RF-6, RF-7 | Cache de ocupación + búsquedas |
| Alertas y Reportes | `alert_report_service` | RF-8, RF-9 | Alertas generadas, reportes agregados |
| Pedidos | `order_service` | RF-13 (más RF-10, 11 indirectamente) | Pedido, PedidoProducto |

### Componentes del Sistema

- **Base de Datos**: PostgreSQL 16 con todas las tablas necesarias (Docker)
- **Bus de Servicios**: ESB (Enterprise Service Bus) para comunicación entre servicios (Docker)
- **Servicios**: Microservicios independientes que se ejecutan desde terminales separadas
- **Cliente de Prueba**: Herramienta para probar la funcionalidad del sistema

## 🚀 Instalación y Configuración

### Prerrequisitos

- Docker y Docker Compose instalados
- Python 3.11+ con las siguientes dependencias:
  - `psycopg2-binary`
  - `socket` (incluido en Python)

### Pasos de Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone <url-del-repositorio>
   cd wms-system
   ```

2. **Instalar dependencias de Python**:
   ```bash
   pip install psycopg2-binary
   ```

3. **Levantar servicios base (DB y Bus)**:
   ```bash
   python start_system.py
   ```

4. **Ejecutar servicios en terminales separadas**:
   ```bash
   # Terminal 1 - Servicio de Productos
   python service/product_service/product_service.py
   
   # Terminal 2 - Servicio de Ubicaciones
   python service/location_service/location_service.py
   
   # Terminal 3 - Servicio de Optimización
   python service/optimization_service/optimization_service.py
   
   # Terminal 4 - Servicio de Movimientos
   python service/movement_service/movement_service.py
   
   # Terminal 5 - Servicio de Visualización
   python service/visualization_service/visualization_service.py
   
   # Terminal 6 - Servicio de Alertas y Reportes
   python service/alert_report_service/alert_report_service.py
   
   # Terminal 7 - Servicio de Pedidos
   python service/order_service/order_service.py
   ```

## 📊 Estructura de la Base de Datos

### Tablas Principales

- **producto**: Almacena información de productos (RF-1)
- **ubicacion**: Gestiona ubicaciones, estantes y zonas (RF-2)
- **stock**: Relación entre productos y ubicaciones
- **movimiento**: Registra movimientos de inventario (RF-5, RF-12)
- **pedido**: Gestiona pedidos de clientes (RF-13)
- **pedido_item**: Items de cada pedido
- **alerta**: Sistema de alertas (RF-8)
- **reporte**: Generación de reportes (RF-9)
- **sugerencia_optimizacion**: Sugerencias de optimización (RF-3, RF-4)
- **cache_visualizacion**: Cache para visualizaciones (RF-6, RF-7)

## 🧪 Pruebas del Sistema

### Cliente de Prueba

El sistema incluye un cliente de prueba que permite interactuar con todos los servicios:

```bash
# Probar todos los servicios
python client/test_client.py

# Probar solo el servicio de productos
python client/test_client.py --service product

# Probar solo el servicio de ubicaciones
python client/test_client.py --service location

# Conectar a un host específico
python client/test_client.py --host 192.168.1.100 --port 5000
```

### Ejemplos de Uso

#### Crear un Producto
```python
{
    "action": "create",
    "product": {
        "nombre": "Laptop HP Pavilion",
        "descripcion": "Laptop de 15 pulgadas",
        "tamanio": 15.5,
        "peso": 2.1,
        "categoria": "Electrónicos",
        "rotacion": "Alta"
    }
}
```

#### Crear una Ubicación
```python
{
    "action": "create",
    "location": {
        "codigo": "A1-B1-C1",
        "nombre": "Pasillo A, Estante 1, Nivel 1",
        "capacidad": 100.0,
        "zona": "A",
        "estante": "B1",
        "tipo": "Almacenamiento"
    }
}
```

## 🔧 Configuración de Servicios

### Variables de Entorno

Los servicios utilizan las siguientes variables de entorno (se pueden configurar en el sistema o usar valores por defecto):

- `DB_HOST`: Host de la base de datos (default: `localhost`)
- `DB_USER`: Usuario de la base de datos (default: `postgres`)
- `DB_PASSWORD`: Contraseña de la base de datos (default: `postgres`)
- `DB_NAME`: Nombre de la base de datos (default: `wms`)

### Puertos

- **Base de Datos**: 5432
- **Bus de Servicios**: 5000
- **Servicios**: Comunicación a través del bus en localhost:5000

## 📁 Estructura del Proyecto

```
wms-system/
├── docker-compose.yml          # Configuración de Docker Compose (solo DB y Bus)
├── start_system.py             # Script de inicio del sistema
├── db/
│   └── init.sql               # Script de inicialización de la BD
├── service/
│   ├── product_service/       # Servicio de Productos
│   ├── location_service/      # Servicio de Ubicaciones
│   ├── optimization_service/  # Servicio de Optimización
│   ├── movement_service/      # Servicio de Movimientos
│   ├── visualization_service/ # Servicio de Visualización
│   ├── alert_report_service/  # Servicio de Alertas y Reportes
│   └── order_service/         # Servicio de Pedidos
├── client/
│   └── test_client.py         # Cliente de prueba
└── readme.md                  # Este archivo
```

## 🚀 Flujo de Ejecución

1. **Iniciar servicios base**:
   ```bash
   python start_system.py
   ```

2. **Ejecutar servicios en terminales separadas**:
   ```bash
   # Terminal 1
   python service/product_service/product_service.py
   
   # Terminal 2
   python service/location_service/location_service.py
   
   # ... y así sucesivamente para cada servicio
   ```

3. **Probar el sistema**:
   ```bash
   python client/test_client.py
   ```

## 🐛 Solución de Problemas

### Servicios no se conectan al bus
- Verificar que el bus esté corriendo: `docker-compose logs bus`
- Verificar que el puerto 5000 esté disponible
- Revisar que los servicios usen `localhost:5000` como dirección del bus

### Errores de base de datos
- Verificar que PostgreSQL esté inicializado: `docker-compose logs db`
- Verificar que el puerto 5432 esté disponible
- Revisar las credenciales de conexión

### Cliente no puede conectarse
- Verificar que el puerto 5000 esté expuesto
- Verificar que al menos un servicio esté registrado en el bus

## 📈 Próximos Pasos

1. **Completar implementación de servicios**: Optimización, Movimientos, Visualización, Alertas y Pedidos
2. **Agregar autenticación y autorización**
3. **Implementar logging centralizado**
4. **Agregar monitoreo y métricas**
5. **Crear interfaz web para administración**

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crear una rama para tu feature
3. Implementar los cambios
4. Agregar pruebas
5. Crear un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo LICENSE para más detalles.