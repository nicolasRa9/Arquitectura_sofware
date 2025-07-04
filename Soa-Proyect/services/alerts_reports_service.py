import socket
import psycopg2

SERVICE_CODE = b'ALERT'

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

def generar_alertas():
    try:
        conn = get_connection()
        cur = conn.cursor()
        # Ubicaciones llenas o casi llenas
        cur.execute("""
            SELECT u.id, u.codigo, u.capacidad, COUNT(a.id)
            FROM ubicaciones u
            LEFT JOIN almacenamiento a ON u.id = a.ubicacion_id
            GROUP BY u.id
        """)
        rows = cur.fetchall()
        alertas = []
        for row in rows:
            capacidad_usada = row[3]  # cantidad de productos
            if capacidad_usada >= 1:  # aquí puedes ajustar el criterio real
                alertas.append(f"Ubicación {row[1]} está llena o casi llena")

        cur.close()
        conn.close()
        return '\n'.join(alertas).encode() if alertas else b'Sin alertas activas'
    except Exception as e:
        return f'Error: {str(e)}'.encode()

def generar_reporte():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM movimientos")
        total_movs = cur.fetchone()[0]

        cur.execute("""
            SELECT p.nombre, COUNT(m.id)
            FROM productos p
            JOIN movimientos m ON p.id = m.producto_id
            GROUP BY p.nombre
            ORDER BY COUNT(m.id) DESC
            LIMIT 3
        """)
        productos_top = cur.fetchall()

        cur.close()
        conn.close()

        reporte = f"Total movimientos: {total_movs}\nTop productos:\n"
        for prod in productos_top:
            reporte += f"- {prod[0]}: {prod[1]} movimientos\n"
        return reporte.strip().encode()
    except Exception as e:
        return f'Error: {str(e)}'.encode()

def handle_request(payload):
    parts = payload.decode().split('|')
    if parts[1].upper() == 'GET':
        return generar_alertas()
    elif parts[1].upper() == 'REPORTE':
        return generar_reporte()
    else:
        return b'Comando no soportado. Usa GET o REPORTE'

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
                print("Servicio ALERT listo y esperando solicitudes del bus...")
                continue

            print("Mensaje recibido del bus, procesando solicitud...")
            payload = data[len(SERVICE_CODE):]
            response = handle_request(payload)
            reply = build_message(SERVICE_CODE, response)
            sock.sendall(reply)

    finally:
        print('Cerrando socket')
        sock.close()

if __name__ == "__main__":
    main()
