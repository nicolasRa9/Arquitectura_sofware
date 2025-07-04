import socket
import psycopg2

SERVICE_CODE = b'UBIC1'

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

def handle_post(parts):
    if len(parts) != 8:
        return b'Error: POST requiere 7 campos'
    try:
        codigo, capacidad, ancho, alto, profundidad, disponible, estante_id = parts[1:]
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO ubicaciones (codigo, capacidad, ancho, alto, profundidad, disponible, estante_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (codigo, float(capacidad), float(ancho), float(alto), float(profundidad), disponible.lower() == 'true', int(estante_id))
        )
        conn.commit()
        cur.close()
        conn.close()
        return b'Ubicacion registrada'
    except Exception as e:
        return f'Error: {str(e)}'.encode()

def handle_get(parts):
    if len(parts) != 2:
        return b'Error: GET requiere 1 campo (id)'
    try:
        id_ = int(parts[1])
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM ubicaciones WHERE id = %s", (id_,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return f'{row[0]}|{row[1]}|{row[2]}|{row[3]}|{row[4]}|{row[5]}|{row[6]}|{row[7]}'.encode()
        else:
            return b'Ubicacion no encontrada'
    except Exception as e:
        return f'Error: {str(e)}'.encode()

def handle_request(payload):
    parts = payload.decode().split('|')
    if parts[0] == 'POST':
        return handle_post(parts)
    elif parts[0] == 'GET':
        return handle_get(parts)
    else:
        return b'Comando no soportado'

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
