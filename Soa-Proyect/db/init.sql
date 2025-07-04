-- Aquí puedes definir las tablas necesarias para productos, movimientos, etc.
CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    ancho FLOAT,
    alto FLOAT,
    profundidad FLOAT,
    cantidad INT
);

CREATE TABLE movimientos (
    id SERIAL PRIMARY KEY,
    producto_id INT REFERENCES productos(id),
    tipo VARCHAR(50),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);