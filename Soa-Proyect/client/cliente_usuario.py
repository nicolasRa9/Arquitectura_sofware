import socket
import json

SERVICE_CODES = {
    "1": "ORDE1",  # Visualizar pedido
    "2": "ORDE2"   # Crear pedido
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

def vista_visualizar_pedido():
    print("\n Visualización de pedido")
    pedido_id = input("Ingrese ID del pedido: ")
    payload = f"ORDER|GET|{pedido_id}"
    send_message(SERVICE_CODES["1"], payload)

def vista_crear_pedido():
    print("\n Creación de nuevo pedido")
    cliente = input("Nombre del cliente: ")
    productos = []
    while True:
        producto_id = input("ID del producto: ")
        cantidad = input("Cantidad: ")
        productos.append({
            "producto_id": int(producto_id),
            "cantidad": int(cantidad)
        })
        continuar = input("¿Agregar otro producto? (s/n): ")
        if continuar.lower() != "s":
            break

    data = {
        "cliente": cliente,
        "productos": productos
    }
    payload = json.dumps(data)
    send_message(SERVICE_CODES["2"], payload)

def main():
    while True:
        print("\n=== MENÚ PEDIDOS ===")
        print("1. Ver pedido")
        print("2. Crear nuevo pedido")
        print("0. Salir")
        op = input("Selecciona una opción: ")

        if op == "1":
            vista_visualizar_pedido()
        elif op == "2":
            vista_crear_pedido()
        elif op == "0":
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    main()
