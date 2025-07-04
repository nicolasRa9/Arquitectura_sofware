import socket
import psycopg2

SERVICE_CODE = b'ORDE1'

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

def consultar_pedido(pedido_id):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Obtener info del pedido
        cur.execute("SELECT * FROM pedidos WHERE id = %s", (pedido_id,))
        pedido = cur.fetchone()
        if not pedido:
            cur.close()
            conn.close()
            return b'Pedido no encontrado'

        # Obtener productos asociados
        cur.execute("""
            SELECT p.nombre, pp.cantidad
            FROM pedido_producto pp
            JOIN productos p ON pp.producto_id = p.id
            WHERE pp.pedido_id = %s
        """, (pedido_id,))
        productos = cur.fetchall()

        cur.close()
        conn.close()

        response = f"Cliente: {pedido[0]}\nEstado: {pedido[1]}\nFecha: {pedido[2]}\nProductos:\n"
        for prod in productos:
            response += f"- {prod[0]} x {prod[1]}\n"
        return response.strip().encode()

    except Exception as e:
        return f'Error: {str(e)}'.encode()

def handle_request(payload):
    parts = payload.decode().split('|')
    if len(parts) == 3 and parts[1].upper() == 'GET':
        return consultar_pedido(int(parts[2]))
    else:
        return b'Comando no soportado. Usa ORDER|GET|id'

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
