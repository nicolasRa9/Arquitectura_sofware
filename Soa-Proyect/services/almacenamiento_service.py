import socket
import psycopg2
import json

SERVICE_CODE = b'SALM1'

def get_connection():
    return psycopg2.connect(
        dbname="wmsdb",
        user="wmsuser",
        password="wmspass",
        host="localhost",
        port="5432"
    )

def build_message(service_code, payload):
    total_len = len(service_code) + len(payload)
    return str(total_len).zfill(5).encode() + service_code + payload

def almacenar_producto(zona_tipo, producto_id):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Obtener datos del producto
        cur.execute("SELECT ancho, alto, profundidad FROM productos WHERE id = %s", (producto_id,))
        prod = cur.fetchone()
        if not prod:
            cur.close()
            conn.close()
            return b'Producto no encontrado'
        prod_ancho, prod_alto, prod_profundidad = prod

        # Buscar ubicaciones en la zona seleccionada
        cur.execute("""
            SELECT u.id, u.capacidad, u.ancho, u.alto, u.profundidad, u.disponible
            FROM ubicaciones u
            JOIN estantes e ON u.estante_id = e.id
            JOIN zonas z ON e.zona_id = z.id
            WHERE z.tipo = %s
            ORDER BY u.id
        """, (zona_tipo,))
        ubicaciones = cur.fetchall()
        if not ubicaciones:
            cur.close()
            conn.close()
            return b'No hay ubicaciones en esa zona'

        # Buscar ubicaciones ocupadas y analizar espacio disponible
        for ubic in ubicaciones:
            ubic_id, capacidad, ancho, alto, profundidad, disponible = ubic
            if not disponible:
                # Sumar el ancho de todos los productos almacenados en esa ubicación
                cur.execute("""
                    SELECT SUM(p.ancho) FROM almacenamiento a
                    JOIN productos p ON a.producto_id = p.id
                    WHERE a.ubicacion_id = %s
                """, (ubic_id,))
                ancho_usado = cur.fetchone()[0] or 0
                if ancho_usado + prod_ancho <= ancho:
                    # Hay espacio suficiente, almacenar aquí
                    cur.execute("""
                        INSERT INTO almacenamiento (producto_id, ubicacion_id) VALUES (%s, %s)
                    """, (producto_id, ubic_id))
                    conn.commit()
                    cur.close()
                    conn.close()
                    return f'Producto almacenado en ubicación ocupada pero con espacio suficiente (ID: {ubic_id})'.encode()

        # Si no hay espacio en ocupadas, buscar la primera ubicación disponible
        for ubic in ubicaciones:
            ubic_id, capacidad, ancho, alto, profundidad, disponible = ubic
            if disponible:
                cur.execute("""
                    INSERT INTO almacenamiento (producto_id, ubicacion_id) VALUES (%s, %s)
                """, (producto_id, ubic_id))
                # Marcar la ubicación como no disponible
                cur.execute("UPDATE ubicaciones SET disponible = FALSE WHERE id = %s", (ubic_id,))
                conn.commit()
                cur.close()
                conn.close()
                return f'Producto almacenado en primer espacio libre (ID: {ubic_id})'.encode()

        cur.close()
        conn.close()
        return b'No hay espacio disponible en la zona seleccionada'
    except Exception as e:
        return f'Error: {str(e)}'.encode()

def handle_request(payload):
    # Espera un mensaje tipo: ZONA|ID_PRODUCTO
    try:
        parts = payload.decode().split('|')
        if len(parts) != 2:
            return b'Formato incorrecto. Usa: ZONA|ID_PRODUCTO'
        zona_tipo = parts[0]
        producto_id = int(parts[1])
        return almacenar_producto(zona_tipo, producto_id)
    except Exception as e:
        return f'Error: {str(e)}'.encode()

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bus_address = ('localhost', 5000)
    print('Conectando a {} puerto {}'.format(*bus_address))
    sock.connect(bus_address)

    try:
        message = build_message(b'sinit', SERVICE_CODE)
        sock.sendall(message)
        sinit = True

        while True:
            length_bytes = sock.recv(5)
            if len(length_bytes) < 5:
                break
            amount_expected = int(length_bytes)

            data = b''
            while len(data) < amount_expected:
                more = sock.recv(amount_expected - len(data))
                if not more:
                    break
                data += more

            if sinit:
                sinit = False
                print("Servicio SALM1 listo y esperando solicitudes del bus...")
                continue

            print("Mensaje recibido del bus, procesando solicitud de almacenamiento...")
            payload = data[len(SERVICE_CODE):]
            response = handle_request(payload)
            reply = build_message(SERVICE_CODE, response)
            sock.sendall(reply)

    finally:
        print('Cerrando socket')
        sock.close()

if __name__ == "__main__":
    main()