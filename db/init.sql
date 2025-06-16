CREATE TABLE producto (
    id_producto SERIAL PRIMARY KEY,
    nombre VARCHAR(255),
    tamanio NUMERIC(10,2),
    peso NUMERIC(10,2),
    categoria VARCHAR(100),
    rotacion VARCHAR(50)
);
CREATE TABLE ubicacion(
    id_ubicacion SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    capacidad NUMERIC(10,2)
);
CREATE TABLE stock(
    id_stock SERIAL PRIMARY KEY,
    id_producto INT REFERENCES producto(id_producto) ON DELETE CASCADE,
    id_ubicacion INT REFERENCES ubicacion(id_ubicacion) ON DELETE CASCADE,
    cantidad INT DEFAULT 0,
    UNIQUE(id_producto,id_ubicacion)
);
CREATE TABLE movimiento(
    id_mov SERIAL PRIMARY KEY,
    id_producto INT REFERENCES producto(id_producto),
    origen INT,
    destino INT,
    cantidad INT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE pedido(
    id_pedido SERIAL PRIMARY KEY,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(30) DEFAULT 'pendiente'
);
CREATE TABLE pedido_item(
    id_pedido_item SERIAL PRIMARY KEY,
    id_pedido INT REFERENCES pedido(id_pedido) ON DELETE CASCADE,
    id_producto INT REFERENCES producto(id_producto) ON DELETE CASCADE,
    cantidad INT
);