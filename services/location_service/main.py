import os, socket, threading, time
#from leer_bus import construir_transaccion, procesar_mensaje

BUS_HOST = os.getenv("BUS_HOST", "bus_service")
BUS_PORT = int(os.getenv("BUS_PORT", "5000"))
SERVICE_NAME = os.getenv("SERVICE_NAME", "SEV02")  # Cambia por el nombre de tu servicio
MSG_SIZE = 1024 # Tamaño del mensaje que se espera recibir

def construir_transaccion(servicio, datos):
    servicio = servicio.ljust(5)  # 5 caracteres
    contenido = servicio + datos
    longitud = str(len(contenido)).zfill(5)
    return longitud + contenido

def procesar_mensaje(data, service_name):
    if len(data) < 10:
        print("error <10")
        return None  # Mensaje inválido
    servicio_destino = data[5:10].strip()
    datos = data[10:]
    print(f"Destino en mensaje: '{servicio_destino}'")
    print(f"Nombre del servicio: '{service_name.strip()}'")
    if servicio_destino == service_name.strip():
        print("error mach")
        return datos
    return None

def procesar_destino(data, service_name):
    if len(data) < 10:
        return None  # Mensaje inválido
    servicio_destino = data[5:10].strip()
    datos = data[10:]
    if servicio_destino == service_name.strip():
        return servicio_destino
    return None

def recv_loop(sock):
        data = sock.recv(MSG_SIZE)
        mensaje = data.decode()
        datos = procesar_mensaje(mensaje, SERVICE_NAME)
        if datos is not None:
            print(f"[{SERVICE_NAME}] Mensaje para mí: {datos}")
            # Aquí puedes agregar la lógica de procesamiento
        else:
            print(f"[{SERVICE_NAME}] Mensaje para otro servicio o inválido.")

def send_loop(sock, destino):

        datos = 'La ubicacion la sabe la mama del nico'
        mensaje = construir_transaccion(destino, datos)
        sock.sendall(mensaje.encode())
        print(f"[{SERVICE_NAME}] -> {mensaje}")
        time.sleep(5)

def main():
    destino = 'CLI01'
    time.sleep(2)  # Espera a que el bus esté listo
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    sock.bind(('localhost', BUS_PORT))
    sock.listen(5)
    print(f"Servicio {SERVICE_NAME} escuchando en puerto {BUS_HOST}...")
    while True:
        conexion, addr = sock.accept()
        with conexion:
            threading.Thread(target=recv_loop, args=(sock,), daemon=True).start()

        send_loop(sock,destino)

if __name__ == "__main__":
    main()
