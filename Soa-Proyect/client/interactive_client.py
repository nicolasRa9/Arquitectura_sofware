import socket

def send_message(service_code, payload):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bus_address = ('localhost', 5000)
    sock.connect(bus_address)
    try:
        message = f"{len(payload)+10:05d}{service_code}{payload}".encode()
        print(f"Enviando: {message}")
        sock.sendall(message)
        amount_expected = int(sock.recv(5))
        data = sock.recv(amount_expected)
        print(f"Respuesta: {data}")
    finally:
        sock.close()

def main():
    while True:
        print("\nOpciones:")
        print("1. Registrar producto")
        print("2. Optimizar almacenamiento")
        print("3. Control de movimientos")
        print("4. Visualización en tiempo real")
        print("5. Alertas y reportes")
        print("0. Salir")
        op = input("Selecciona una opción: ")
        if op == "1":
            payload = input("Datos del producto: ")
            send_message("product_serv", payload)
        elif op == "2":
            payload = input("Datos para optimización: ")
            send_message("storage_opt", payload)
        elif op == "3":
            payload = input("Datos de movimiento: ")
            send_message("move_ctrl", payload)
        elif op == "4":
            payload = input("Parámetros de visualización: ")
            send_message("visual_serv", payload)
        elif op == "5":
            payload = input("Parámetros de alerta/reporte: ")
            send_message("alert_serv", payload)
        elif op == "0":
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    main()