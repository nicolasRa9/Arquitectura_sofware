import socket
import psycopg2
from datetime import datetime

SERVICE_CODE = b'OPTI1'

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

def sugerir_ubicacion(producto_id):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Obtener dimensiones del producto
        cur.execute("SELECT ancho, alto, profundidad FROM productos WHERE id = %s", (producto_id,))
        producto = cur.fetchone()
        if not producto:
            return b'Producto no encontrado'

        volumen_producto = producto[0] * producto[1] * producto[2]

        # Buscar ubicación disponible con suficiente capacidad
        cur.execute("""
            SELECT id, capacidad FROM ubicaciones
            WHERE disponible = true AND capacidad >= %s
            ORDER BY capacidad ASC
            LIMIT 1
        """, (volumen_producto,))
        ubicacion = cur.fetchone()
        cur.close()
        conn.close()

        if ubicacion:
            return f'Ubicacion sugerida: {ubicacion[0]} (capacidad: {ubicacion[1]})'.encode()
        else:
            return b'No hay ubicaciones disponibles'

    except Exception as e:
        return f'Error: {str(e)}'.encode()

def reubicar_producto(producto_id):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Buscar ubicación actual del producto
        cur.execute("SELECT id, ubicacion_id FROM almacenamiento WHERE producto_id = %s", (producto_id,))
        almacenamiento = cur.fetchone()
        if not almacenamiento:
            return b'Producto no almacenado actualmente'

        # Marcar ubicación actual como disponible
        cur.execute("UPDATE ubicaciones SET disponible = true WHERE id = %s", (almacenamiento[1],))

        # Buscar nueva ubicación
        respuesta = sugerir_ubicacion(producto_id)
        if not respuesta.startswith(b'Ubicacion sugerida:'):
            return respuesta

        nueva_ubicacion_id = int(respuesta.decode().split()[2])
        now = datetime.now()

        # Insertar nueva ubicación
        cur.execute("""
            UPDATE almacenamiento SET ubicacion_id = %s, fecha_reubicacion = %s
            WHERE id = %s
        """, (nueva_ubicacion_id, now, almacenamiento[0]))

        # Marcar nueva ubicación como ocupada
        cur.execute("UPDATE ubicaciones SET disponible = false WHERE id = %s", (nueva_ubicacion_id,))
        conn.commit()
        cur.close()
        conn.close()
        return f'Producto reubicado a ubicación {nueva_ubicacion_id}'.encode()

    except Exception as e:
        return f'Error: {str(e)}'.encode()

def handle_request(payload):
    try:
        parts = payload.decode().split('|')
        if len(parts) != 3:
            return b'Formato invalido. Usa: OPTIM|SUGERIR|id o OPTIM|REUBICAR|id'

        accion, producto_id = parts[1], int(parts[2])
        if accion.upper() == 'SUGERIR':
            return sugerir_ubicacion(producto_id)
        elif accion.upper() == 'REUBICAR':
            return reubicar_producto(producto_id)
        else:
            return b'Accion no reconocida'
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
                continue

            payload = data[len(SERVICE_CODE):]
            response = handle_request(payload)
            reply = build_message(SERVICE_CODE, response)
            sock.sendall(reply)

    finally:
        print('Cerrando socket')
        sock.close()

if __name__ == "__main__":
    main()
