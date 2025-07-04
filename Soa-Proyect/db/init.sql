-- Tabla de productos
CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    ancho FLOAT,
    alto FLOAT,
    profundidad FLOAT,
    cantidad INT
);

-- Tabla de ubicaciones físicas del almacén
CREATE TABLE ubicaciones (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    capacidad FLOAT,
    ancho FLOAT,
    alto FLOAT,
    profundidad FLOAT,
    disponible BOOLEAN DEFAULT TRUE,
    estante_id INT
);

-- Tabla de movimientos (ingreso / salida)
CREATE TABLE movimientos (
    id SERIAL PRIMARY KEY,
    producto_id INT REFERENCES productos(id) ON DELETE CASCADE,
    tipo VARCHAR(50), -- 'ingreso' o 'salida'
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    observaciones TEXT
);

-- Tabla de almacenamiento (relación entre producto y ubicación)
CREATE TABLE almacenamiento (
    id SERIAL PRIMARY KEY,
    producto_id INT REFERENCES productos(id) ON DELETE CASCADE,
    ubicacion_id INT REFERENCES ubicaciones(id),
    fecha_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_reubicacion TIMESTAMP
);

-- Tabla de estantes
CREATE TABLE estantes (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    cant_espacios INT,
    zona_id INT
);

-- Tabla de zonas
CREATE TABLE zonas (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    tipo VARCHAR(50)
);

-- Tabla de pedidos
CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    nombre_cliente VARCHAR(255),
    estado VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de productos por pedido
CREATE TABLE pedido_producto (
    id SERIAL PRIMARY KEY,
    pedido_id INT REFERENCES pedidos(id) ON DELETE CASCADE,
    producto_id INT REFERENCES productos(id),
    cantidad INT
);
