-- Script de inicialización de la base de datos WMS
-- Crea todas las tablas necesarias para el sistema de gestión de almacén

-- Tabla de Productos (RF-1)
CREATE TABLE IF NOT EXISTS producto (
    id_producto SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    tamanio NUMERIC(10,2) NOT NULL,
    peso NUMERIC(10,2) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    rotacion VARCHAR(50) NOT NULL CHECK (rotacion IN ('Alta', 'Media', 'Baja')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Ubicaciones (RF-2)
CREATE TABLE IF NOT EXISTS ubicacion (
    id_ubicacion SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(255),
    capacidad NUMERIC(10,2) NOT NULL,
    zona VARCHAR(100),
    estante VARCHAR(50),
    tipo VARCHAR(50) DEFAULT 'Almacenamiento',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Stock (Relación Producto-Ubicación)
CREATE TABLE IF NOT EXISTS stock (
    id_stock SERIAL PRIMARY KEY,
    id_producto INT REFERENCES producto(id_producto) ON DELETE CASCADE,
    id_ubicacion INT REFERENCES ubicacion(id_ubicacion) ON DELETE CASCADE,
    cantidad INT DEFAULT 0,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(id_producto, id_ubicacion)
);

-- Tabla de Movimientos (RF-5, RF-12)
CREATE TABLE IF NOT EXISTS movimiento (
    id_movimiento SERIAL PRIMARY KEY,
    id_producto INT REFERENCES producto(id_producto),
    origen INT REFERENCES ubicacion(id_ubicacion),
    destino INT REFERENCES ubicacion(id_ubicacion),
    cantidad INT NOT NULL,
    tipo_movimiento VARCHAR(50) DEFAULT 'Transferencia',
    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario VARCHAR(100),
    estado VARCHAR(30) DEFAULT 'Completado'
);

-- Tabla de Pedidos (RF-13)
CREATE TABLE IF NOT EXISTS pedido (
    id_pedido SERIAL PRIMARY KEY,
    numero_pedido VARCHAR(50) UNIQUE,
    fecha_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(30) DEFAULT 'Pendiente',
    cliente VARCHAR(255),
    prioridad VARCHAR(20) DEFAULT 'Normal',
    fecha_entrega_estimada DATE
);

-- Tabla de Items de Pedido
CREATE TABLE IF NOT EXISTS pedido_item (
    id_pedido_item SERIAL PRIMARY KEY,
    id_pedido INT REFERENCES pedido(id_pedido) ON DELETE CASCADE,
    id_producto INT REFERENCES producto(id_producto) ON DELETE CASCADE,
    cantidad INT NOT NULL,
    cantidad_entregada INT DEFAULT 0,
    precio_unitario NUMERIC(10,2)
);

-- Tabla de Alertas (RF-8)
CREATE TABLE IF NOT EXISTS alerta (
    id_alerta SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    mensaje TEXT NOT NULL,
    id_producto INT REFERENCES producto(id_producto),
    id_ubicacion INT REFERENCES ubicacion(id_ubicacion),
    fecha_alerta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(30) DEFAULT 'Activa',
    prioridad VARCHAR(20) DEFAULT 'Media'
);

-- Tabla de Reportes (RF-9)
CREATE TABLE IF NOT EXISTS reporte (
    id_reporte SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    contenido JSON,
    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parametros JSON
);

-- Tabla de Sugerencias de Optimización (RF-3, RF-4)
CREATE TABLE IF NOT EXISTS sugerencia_optimizacion (
    id_sugerencia SERIAL PRIMARY KEY,
    id_producto INT REFERENCES producto(id_producto),
    id_ubicacion_origen INT REFERENCES ubicacion(id_ubicacion),
    id_ubicacion_destino INT REFERENCES ubicacion(id_ubicacion),
    tipo_sugerencia VARCHAR(50),
    descripcion TEXT,
    beneficio_estimado NUMERIC(10,2),
    fecha_sugerencia TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(30) DEFAULT 'Pendiente'
);

-- Tabla de Cache de Visualización (RF-6, RF-7)
CREATE TABLE IF NOT EXISTS cache_visualizacion (
    id_cache SERIAL PRIMARY KEY,
    tipo_cache VARCHAR(50) NOT NULL,
    datos JSON NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expira_en TIMESTAMP
);

-- Índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_producto_categoria ON producto(categoria);
CREATE INDEX IF NOT EXISTS idx_producto_rotacion ON producto(rotacion);
CREATE INDEX IF NOT EXISTS idx_ubicacion_zona ON ubicacion(zona);
CREATE INDEX IF NOT EXISTS idx_stock_producto ON stock(id_producto);
CREATE INDEX IF NOT EXISTS idx_stock_ubicacion ON stock(id_ubicacion);
CREATE INDEX IF NOT EXISTS idx_movimiento_fecha ON movimiento(fecha_movimiento);
CREATE INDEX IF NOT EXISTS idx_pedido_estado ON pedido(estado);
CREATE INDEX IF NOT EXISTS idx_alerta_fecha ON alerta(fecha_alerta);
CREATE INDEX IF NOT EXISTS idx_alerta_estado ON alerta(estado);

-- Datos de ejemplo para pruebas
INSERT INTO producto (nombre, descripcion, tamanio, peso, categoria, rotacion) VALUES
('Laptop HP Pavilion', 'Laptop de 15 pulgadas', 15.5, 2.1, 'Electrónicos', 'Alta'),
('Mouse Logitech', 'Mouse inalámbrico', 0.1, 0.2, 'Periféricos', 'Media'),
('Teclado Mecánico', 'Teclado gaming RGB', 0.3, 0.8, 'Periféricos', 'Alta'),
('Monitor Samsung', 'Monitor 24 pulgadas', 24.0, 3.5, 'Electrónicos', 'Media'),
('Cable HDMI', 'Cable HDMI 2 metros', 0.05, 0.1, 'Accesorios', 'Baja')
ON CONFLICT DO NOTHING;

INSERT INTO ubicacion (codigo, nombre, capacidad, zona, estante) VALUES
('A1-B1-C1', 'Pasillo A, Estante 1, Nivel 1', 100.0, 'A', 'B1'),
('A1-B1-C2', 'Pasillo A, Estante 1, Nivel 2', 100.0, 'A', 'B1'),
('A1-B2-C1', 'Pasillo A, Estante 2, Nivel 1', 150.0, 'A', 'B2'),
('B1-B1-C1', 'Pasillo B, Estante 1, Nivel 1', 200.0, 'B', 'B1'),
('B1-B2-C1', 'Pasillo B, Estante 2, Nivel 1', 200.0, 'B', 'B2')
ON CONFLICT DO NOTHING;

-- Insertar stock inicial
INSERT INTO stock (id_producto, id_ubicacion, cantidad) VALUES
(1, 1, 5),
(2, 2, 20),
(3, 3, 10),
(4, 4, 3),
(5, 5, 50)
ON CONFLICT (id_producto, id_ubicacion) DO UPDATE SET 
cantidad = EXCLUDED.cantidad,
fecha_actualizacion = CURRENT_TIMESTAMP; 