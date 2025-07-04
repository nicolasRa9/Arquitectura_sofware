import socket
import psycopg2

SERVICE_CODE = b'VISU1'

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

def visualizar_mapa():
    try:
        conn = get_connection()
        cur = conn.cursor()
        # Obtener zonas
        cur.execute("SELECT id, tipo FROM zonas ORDER BY id")
        zonas = cur.fetchall()
        if not zonas:
            cur.close()
            conn.close()
            return b'Almacen sin zonas'

        result = "\n=== MAPA DEL ALMACEN ===\n"
        for zona_id, zona_tipo in zonas:
            result += f"\nZona: {zona_tipo}\n"
            # Obtener estantes de la zona
            cur.execute("SELECT id, codigo FROM estantes WHERE zona_id = %s ORDER BY id", (zona_id,))
            estantes = cur.fetchall()
            if not estantes:
                result += "  (Sin estantes)\n"
                continue
            for estante_id, estante_codigo in estantes:
                result += f"  Estante: {estante_codigo}\n"
                # Obtener ubicaciones del estante
                cur.execute("""
                    SELECT id, codigo, disponible 
                    FROM ubicaciones 
                    WHERE estante_id = %s 
                    ORDER BY id
                """, (estante_id,))
                ubicaciones = cur.fetchall()
                if not ubicaciones:
                    result += "    (Sin ubicaciones)\n"
                    continue
                # Dibuja las ubicaciones como una línea
                result += "    "
                for ubic in ubicaciones:
                    simbolo = "[ ]" if ubic[2] else "[X]"
                    result += f"{simbolo}"
                result += "\n"
        cur.close()
        conn.close()
        return result.strip().encode()
    except Exception as e:
        return f'Error: {str(e)}'.encode()

def buscar_producto(producto_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT u.id, u.codigo FROM almacenamiento a
            JOIN ubicaciones u ON a.ubicacion_id = u.id
            WHERE a.producto_id = %s
        """, (producto_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return f'Producto {producto_id} en Ubicacion ID:{row[0]} Cod:{row[1]}'.encode()
        else:
            return b'Producto no ubicado actualmente'
    except Exception as e:
        return f'Error: {str(e)}'.encode()

def productos_almacenados_todos():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT p.id, p.nombre, p.ancho, p.alto, p.profundidad, p.cantidad, u.codigo as ubicacion
            FROM almacenamiento a
            JOIN productos p ON a.producto_id = p.id
            JOIN ubicaciones u ON a.ubicacion_id = u.id
            ORDER BY u.codigo, p.id
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        if not rows:
            return b'No hay productos almacenados'
        result = "\n=== PRODUCTOS ALMACENADOS ===\n"
        for row in rows:
            result += f"ID:{row[0]} | Nombre:{row[1]} | Dim:{row[2]}x{row[3]}x{row[4]} | Cantidad:{row[5]} | Ubicación:{row[6]}\n"
        return result.strip().encode()
    except Exception as e:
        return f'Error: {str(e)}'.encode()

def productos_por_estante(estante_codigo):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM estantes WHERE id = %s", (estante_codigo,))
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            return b'Estante no encontrado'
        estante_id = row[0]
        cur.execute("""
            SELECT p.id, p.nombre, p.ancho, p.alto, p.profundidad, p.cantidad, u.codigo as ubicacion
            FROM almacenamiento a
            JOIN productos p ON a.producto_id = p.id
            JOIN ubicaciones u ON a.ubicacion_id = u.id
            WHERE u.estante_id = %s
            ORDER BY u.codigo, p.id
        """, (estante_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        if not rows:
            return b'No hay productos en ese estante'
        result = f"\n=== PRODUCTOS EN ESTANTE {estante_codigo} ===\n"
        for row in rows:
            result += f"ID:{row[0]} | Nombre:{row[1]} | Dim:{row[2]}x{row[3]}x{row[4]} | Cantidad:{row[5]} | Ubicación:{row[6]}\n"
        return result.strip().encode()
    except Exception as e:
        return f'Error: {str(e)}'.encode()

def productos_por_zona(zona_tipo):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM zonas WHERE tipo = %s", (zona_tipo,))
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            return b'Zona no encontrada'
        zona_id = row[0]
        cur.execute("""
            SELECT p.id, p.nombre, p.ancho, p.alto, p.profundidad, p.cantidad, u.codigo as ubicacion, e.codigo as estante
            FROM almacenamiento a
            JOIN productos p ON a.producto_id = p.id
            JOIN ubicaciones u ON a.ubicacion_id = u.id
            JOIN estantes e ON u.estante_id = e.id
            WHERE e.zona_id = %s
            ORDER BY e.codigo, u.codigo, p.id
        """, (zona_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        if not rows:
            return b'No hay productos en esa zona'
        result = f"\n=== PRODUCTOS EN ZONA {zona_tipo} ===\n"
        for row in rows:
            result += f"ID:{row[0]} | Nombre:{row[1]} | Dim:{row[2]}x{row[3]}x{row[4]} | Cantidad:{row[5]} | Ubicación:{row[6]} | Estante:{row[7]}\n"
        return result.strip().encode()
    except Exception as e:
        return f'Error: {str(e)}'.encode()

def handle_request(payload):
    try:
        parts = payload.decode().split('|')
        if parts[1].upper() == 'MAPA':
            return visualizar_mapa()
        elif parts[1].upper() == 'BUSCAR' and len(parts) == 3:
            return buscar_producto(int(parts[2]))
        elif parts[1].upper() == 'PRODUCTOS':
            if len(parts) == 3 and parts[2].upper() == 'TODOS':
                return productos_almacenados_todos()
            elif len(parts) == 4 and parts[2].upper() == 'ESTANTE':
                return productos_por_estante(parts[3])
            elif len(parts) == 4 and parts[2].upper() == 'ZONA':
                return productos_por_zona(parts[3])
            else:
                return b'Formato incorrecto. Usa: VISUA|PRODUCTOS|TODOS o VISUA|PRODUCTOS|ESTANTE|codigo o VISUA|PRODUCTOS|ZONA|tipo'
        else:
            return b'Comando no reconocido o incompleto'
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
