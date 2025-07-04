# servicio_almacen.py
import socket
import psycopg2
import json

SERVICE_CODE = b'ALMCN'

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

def crear_zona(cur, tipo):
    cur.execute("INSERT INTO zonas (tipo) VALUES (%s) RETURNING id", (tipo,))
    return cur.fetchone()[0]

def crear_estante(cur, zona_id, codigo, cant_espacios):
    cur.execute(
        "INSERT INTO estantes (codigo, cant_espacios, zona_id) VALUES (%s, %s, %s) RETURNING id",
        (codigo, cant_espacios, zona_id)
    )
    return cur.fetchone()[0]

def crear_ubicacion(cur, codigo, capacidad, ancho, alto, profundidad, disponible, estante_id):
    cur.execute(
        "INSERT INTO ubicaciones (codigo, capacidad, ancho, alto, profundidad, disponible, estante_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (codigo, capacidad, ancho, alto, profundidad, disponible, estante_id)
    )

def handle_request(payload):
    try:
        data = json.loads(payload.decode())
        zonas = data["zonas"]
        ancho = float(data["ancho"])
        alto = float(data["alto"])
        profundidad = float(data["profundidad"])
        capacidad = int(data["capacidad"])

        conn = get_connection()
        cur = conn.cursor()

        for idx_z, zona in enumerate(zonas):
            tipo = zona["tipo"]
            zona_id = crear_zona(cur, tipo)
            for idx_e, estante in enumerate(zona["estantes"]):
                codigo_estante = f"Z{idx_z+1}-E{idx_e+1}"
                cant_espacios = estante["cant_espacios"]
                estante_id = crear_estante(cur, zona_id, codigo_estante, cant_espacios)
                for idx_u in range(cant_espacios):
                    codigo_ubic = f"{codigo_estante}-U{idx_u+1}"
                    crear_ubicacion(cur, codigo_ubic, capacidad, ancho, alto, profundidad, True, estante_id)

        conn.commit()
        cur.close()
        conn.close()
        return b'Almacen configurado exitosamente'
    except Exception as e:
        return f'Error: {str(e)}'.encode()

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bus_address = ('localhost', 5000)
    sock.connect(bus_address)

    try:
        sock.sendall(build_message(b'sinit', SERVICE_CODE))
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
                print("Servicio ALMCN registrado y listo")
                continue

            print("Procesando solicitud de creaci\u00f3n de almac\u00e9n...")
            payload = data[len(SERVICE_CODE):]
            response = handle_request(payload)
            sock.sendall(build_message(SERVICE_CODE, response))
    finally:
        sock.close()

if __name__ == "__main__":
    main()
