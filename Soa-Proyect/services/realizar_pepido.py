import socket
import psycopg2
import json
from datetime import datetime

SERVICE_CODE = b'ORDE2'

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

def crear_pedido(cur, cliente, productos):
    cur.execute(
        "INSERT INTO pedidos (nombre_cliente, estado) VALUES (%s, %s) RETURNING id",
        (cliente, "pendiente")
    )
    pedido_id = cur.fetchone()[0]

    for item in productos:
        cur.execute(
            "INSERT INTO pedido_producto (pedido_id, producto_id, cantidad) VALUES (%s, %s, %s)",
            (pedido_id, item["producto_id"], item["cantidad"])
        )
    return pedido_id

def handle_request(payload):
    try:
        data = json.loads(payload.decode())
        cliente = data["cliente"]
        productos = data["productos"]

        conn = get_connection()
        cur = conn.cursor()
        pedido_id = crear_pedido(cur, cliente, productos)
        conn.commit()
        cur.close()
        conn.close()

        return f"Pedido #{pedido_id} creado correctamente".encode()

    except Exception as e:
        return f"Error: {str(e)}".encode()

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bus_address = ('localhost', 5000)
    print('Conectando al bus en {}:{}'.format(*bus_address))
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
                print("Servicio ORDE1 registrado y esperando solicitudes...")
                continue

            payload = data[len(SERVICE_CODE):]
            response = handle_request(payload)
            reply = build_message(SERVICE_CODE, response)
            sock.sendall(reply)

    finally:
        print("Cerrando socket del servicio ORDE1")
        sock.close()

if __name__ == "__main__":
    main()
