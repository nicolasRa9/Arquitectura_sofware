import psycopg2
from faker import Faker
from random import randint, choice

fake = Faker()

def get_connection():
    return psycopg2.connect(
        dbname="wmsdb",
        user="wmsuser",
        password="wmspass",
        host="localhost",
        port="5432"
    )

def poblar_productos_y_pedidos():
    conn = get_connection()
    cur = conn.cursor()

    # === Insertar productos (si no existen) ===
    print("✅ Insertando productos...")
    for _ in range(10):
        cur.execute("""
            INSERT INTO productos (nombre, ancho, alto, profundidad, cantidad)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            fake.word(),
            round(fake.random_number(digits=2)/10, 2),
            round(fake.random_number(digits=2)/10, 2),
            round(fake.random_number(digits=2)/10, 2),
            randint(1, 100)
        ))

    # Obtener todos los productos disponibles
    cur.execute("SELECT id FROM productos")
    producto_ids = [row[0] for row in cur.fetchall()]

    # === Crear pedidos con productos ===
    print("✅ Insertando pedidos y asignando productos...")
    for _ in range(5):
        cur.execute("""
            INSERT INTO pedidos (nombre_cliente, estado)
            VALUES (%s, %s)
            RETURNING id
        """, (
            fake.name(),
            choice(["pendiente", "procesando", "completado"])
        ))
        pedido_id = cur.fetchone()[0]

        # Asignar entre 1 y 4 productos por pedido
        for _ in range(randint(1, 4)):
            producto_id = choice(producto_ids)
            cantidad = randint(1, 20)
            cur.execute("""
                INSERT INTO pedido_producto (pedido_id, producto_id, cantidad)
                VALUES (%s, %s, %s)
            """, (pedido_id, producto_id, cantidad))

    conn.commit()
    cur.close()
    conn.close()
    print("🎉 ¡Datos de productos y pedidos insertados correctamente!")

if __name__ == "__main__":
    poblar_productos_y_pedidos()
