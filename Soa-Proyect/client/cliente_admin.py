import socket
import json

SERVICE_CODES = {
    "1": "PROD1",
    "2": "OPTI1",
    "3": "MOVE1",
    "4": "VISU1",
    "5": "ALERT",
    "6": "UBIC1",
    "7": "ORDE1",
    "8": "ALMCN",
    "9": "SALM1"  # Servicio de almacenamiento de producto
}

def send_message(service_code, payload):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bus_address = ('localhost', 5000)
    sock.connect(bus_address)
    try:
        message = f"{len(payload)+10:05d}{service_code}{payload}".encode()
        print(f"\n Enviando: {message}")
        sock.sendall(message)
        amount_expected = int(sock.recv(5))
        data = sock.recv(amount_expected)
        print(f"\n Respuesta: {data.decode()}")
    finally:
        sock.close()

# === Vistas por funcionalidad ===

def vista_registrar_producto():
    print("\n Registrar nuevo producto")
    nombre = input("Nombre: ")
    ancho = input("Ancho: ")
    alto = input("Alto: ")
    profundidad = input("Profundidad: ")
    cantidad = input("Cantidad: ")
    payload = f"POST|{nombre}|{ancho}|{alto}|{profundidad}|{cantidad}"
    send_message(SERVICE_CODES["1"], payload)

def vista_optimizar():
    print("\n Optimización")
    tipo = input("Tipo de acción (SUGERIR o REUBICAR): ").upper()
    producto_id = input("ID del producto: ")
    payload = f"OPTIM|{tipo}|{producto_id}"
    send_message(SERVICE_CODES["2"], payload)

def vista_movimiento():
    print("\n Control de movimientos")
    id_producto = input("ID producto: ")
    tipo = input("Tipo (ingreso/salida): ")
    fecha = input("Fecha (YYYY-MM-DD HH:MM:SS): ")
    observaciones = input("Observaciones: ")
    payload = f"POST|{id_producto}|{tipo}|{fecha}|{observaciones}"
    send_message(SERVICE_CODES["3"], payload)

def vista_visualizacion():
    print("\nVisualización del almacén")
    print("1. Ver mapa del almacén")
    print("2. Buscar producto por ID")
    print("3. Ver todos los productos almacenados")
    print("4. Ver productos por estante")
    print("5. Ver productos por zona")
    op = input("Selecciona una opción: ")
    if op == "1":
        payload = "VISUA|MAPA"
    elif op == "2":
        producto_id = input("ID del producto: ")
        payload = f"VISUA|BUSCAR|{producto_id}"
    elif op == "3":
        payload = "VISUA|PRODUCTOS|TODOS"
    elif op == "4":
        estante_codigo = input("Código del estante: ")
        payload = f"VISUA|PRODUCTOS|ESTANTE|{estante_codigo}"
    elif op == "5":
        zona_tipo = input("Tipo de zona: ")
        payload = f"VISUA|PRODUCTOS|ZONA|{zona_tipo}"
    else:
        print("Opción inválida")
        return
    send_message(SERVICE_CODES["4"], payload)

def vista_alertas():
    print("\n Alertas y reportes")
    op = input("1. Ver alertas\n2. Ver reporte\nOpción: ")
    if op == "1":
        payload = "ALERT|GET"
    elif op == "2":
        payload = "ALERT|REPORTE"
    else:
        print("Opción inválida")
        return
    send_message(SERVICE_CODES["5"], payload)

def vista_ubicaciones():
    print("\n Gestión de ubicaciones")
    op = input("1. Registrar ubicación\n2. Consultar ubicación\nOpción: ")
    if op == "1":
        codigo = input("Código: ")
        capacidad = input("Capacidad: ")
        ancho = input("Ancho: ")
        alto = input("Alto: ")
        profundidad = input("Profundidad: ")
        disponible = input("Disponible (true/false): ")
        estante_id = input("ID del estante: ")
        payload = f"POST|{codigo}|{capacidad}|{ancho}|{alto}|{profundidad}|{disponible}|{estante_id}"
    elif op == "2":
        id_ = input("ID ubicación: ")
        payload = f"GET|{id_}"
    else:
        print("Opción inválida")
        return
    send_message(SERVICE_CODES["6"], payload)

def vista_ordenes():
    print("\n Consulta de pedido")
    pedido_id = input("ID del pedido: ")
    payload = f"ORDER|GET|{pedido_id}"
    send_message(SERVICE_CODES["7"], payload)

def vista_crear_almacen():
    print("\n Crear almacén")
    zonas = []
    n_zonas = int(input("¿Cuántas zonas tiene el almacén? "))
    for i in range(n_zonas):
        tipo_zona = input(f"Tipo de la zona #{i+1} (ej: refrigerado, general): ")
        n_estantes = int(input(f"¿Cuántos estantes tiene la zona #{i+1}? "))
        estantes = []
        for j in range(n_estantes):
            nombre_estante = input(f"  Nombre del estante #{j+1} (para identificar en base): ")
            espacios = int(input(f"    ¿Cuántos espacios tiene '{nombre_estante}'? "))
            estantes.append({
                "nombre": nombre_estante,
                "cant_espacios": espacios
            })
        zonas.append({
            "tipo": tipo_zona,
            "estantes": estantes
        })

    print("\n=== Dimensiones estándar por ubicación ===")
    ancho = float(input("Ancho estándar: "))
    alto = float(input("Alto estándar: "))
    profundidad = float(input("Profundidad estándar: "))
    capacidad = int(input("Capacidad por espacio: "))

    data = {
        "zonas": zonas,
        "ancho": ancho,
        "alto": alto,
        "profundidad": profundidad,
        "capacidad": capacidad
    }
    payload = json.dumps(data)
    send_message(SERVICE_CODES["8"], payload)

def vista_almacenar_producto():
    print("\n Almacenar producto en ubicación")
    zona = input("Zona destino (tipo): ")
    producto_id = input("ID del producto a almacenar: ")
    payload = f"{zona}|{producto_id}"
    send_message(SERVICE_CODES["9"], payload)

# === Menú principal ===

def main():
    while True:
        print("\n=== MENÚ PRINCIPAL ===")
        print("1. Registrar producto")
        print("2. Optimizar almacenamiento")
        print("3. Control de movimientos")
        print("4. Visualización")
        print("5. Alertas y reportes")
        print("6. Gestión de ubicaciones")
        print("7. Consulta de pedidos")
        print("8. Crear almacén")
        print("9. Almacenar producto en ubicación")
        print("0. Salir")
        op = input("Selecciona una opción: ")

        if op == "1":
            vista_registrar_producto()
        elif op == "2":
            vista_optimizar()
        elif op == "3":
            vista_movimiento()
        elif op == "4":
            vista_visualizacion()
        elif op == "5":
            vista_alertas()
        elif op == "6":
            vista_ubicaciones()
        elif op == "7":
            vista_ordenes()
        elif op == "8":
            vista_crear_almacen()
        elif op == "9":
            vista_almacenar_producto()
        elif op == "0":
            break
        else:
            print("❌ Opción inválida.")

if __name__ == "__main__":
    main()
