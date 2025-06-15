CREATE TABLE producto (
    id_producto SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tamanio VARCHAR(50) NOT NULL,
    peso DECIMAL(10,2) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    rotacion VARCHAR(20) NOT NULL
);

CREATE TABLE ubicacion (
    id_ubicacion SERIAL PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    capacidad INTEGER NOT NULL CHECK (capacidad > 0),
    disponible BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE almacenamiento (
    id_almacenamiento SERIAL PRIMARY KEY,
    id_producto INTEGER NOT NULL REFERENCES producto(id_producto) ON DELETE CASCADE ON UPDATE CASCADE,
    id_ubicacion INTEGER NOT NULL REFERENCES ubicacion(id_ubicacion) ON DELETE CASCADE ON UPDATE CASCADE,
    fecha_ingreso TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_reubicacion TIMESTAMP
);

CREATE TABLE movimiento (
    id_movimiento SERIAL PRIMARY KEY,
    id_producto INTEGER NOT NULL REFERENCES producto(id_producto) ON DELETE CASCADE ON UPDATE CASCADE,
    tipo_movimiento VARCHAR(30) NOT NULL,
    fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    observaciones VARCHAR(255)
);

CREATE TABLE pedido (
    id_pedido SERIAL PRIMARY KEY,
    nombre_cliente VARCHAR(100) NOT NULL,
    estado VARCHAR(30) NOT NULL,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pedido_producto (
    id_pedido_producto SERIAL PRIMARY KEY,
    id_pedido INTEGER NOT NULL REFERENCES pedido(id_pedido) ON DELETE CASCADE ON UPDATE CASCADE,
    id_producto INTEGER NOT NULL REFERENCES producto(id_producto) ON DELETE CASCADE ON UPDATE CASCADE,
    cantidad INTEGER NOT NULL CHECK (cantidad > 0)
);