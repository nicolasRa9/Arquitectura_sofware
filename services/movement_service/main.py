import os, socket, threading, time

BUS_HOST = os.getenv("BUS_HOST", "bus_service")
BUS_PORT = int(os.getenv("BUS_PORT", "5000"))
SERVICE_NAME = os.getenv("SERVICE_NAME", "SEV02")
MSG_SIZE = 1024

def construir_transaccion(servicio, datos):
    servicio = servicio.ljust(5)
    contenido = servicio + datos
    longitud = str(len(contenido)).zfill(5)
    return longitud + contenido

def procesar_mensaje(data, service_name):
    if len(data) < 10:
        print("error <10")
        return None
    servicio_destino = data[5:10].strip()
    datos = data[10:]
    if servicio_destino == service_name.strip():
        print("Mensaje recibido para mí")
        return datos
    return None

def recv_loop(sock):
    print("mensaje recibido")
    while True:
        data = sock.recv(MSG_SIZE)
        if not data:
            break
        mensaje = data.decode()
        datos = procesar_mensaje(mensaje, SERVICE_NAME)
        if datos is not None:
            print(f"[{SERVICE_NAME}] Mensaje para mí: {datos}")
        else:
            print(f"[{SERVICE_NAME}] Mensaje para otro servicio o inválido.")

def send_loop(sock, destino):
    while True:
        datos = 'La ubicacion la sabe la mama del nico'
        mensaje = construir_transaccion(destino, datos)
        sock.sendall(mensaje.encode())
        print(f"[{SERVICE_NAME}] -> {mensaje}")
        time.sleep(5)

def main():
    destino = 'SEV02'
    time.sleep(2)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((BUS_HOST, BUS_PORT))
    print(f"[{SERVICE_NAME}] Registrado en el bus.")
    threading.Thread(target=recv_loop, args=(sock,), daemon=True).start()
    print(f"[{SERVICE_NAME}] Esperando mensajes...")
    send_loop(sock, destino)

if __name__ == "__main__":
    main()