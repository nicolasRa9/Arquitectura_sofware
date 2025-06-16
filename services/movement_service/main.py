import os, socket, threading, time, random, string
from base.leer_bus import construir_transaccion, procesar_mensaje, procesar_destino

BUS_HOST = os.getenv("BUS_HOST", "bus_service")
BUS_PORT = int(os.getenv("BUS_PORT", "5000"))
SERVICE_NAME = os.getenv("SERVICE_NAME", "SEV09")  # Cambia por el nombre de tu servicio
MSG_SIZE = 1024 # Tamaño del mensaje que se espera recibir


def recv_loop(sock):
    while True:
        data = sock.recv(MSG_SIZE)
        if not data:
            break
        mensaje = data.decode()
        datos = procesar_mensaje(mensaje, SERVICE_NAME)
        if datos is not None:
            print(f"[{SERVICE_NAME}] Mensaje para mí: {datos}")
            # Aquí puedes agregar la lógica de procesamiento
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
    time.sleep(2)  # Espera a que el bus esté listo
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((BUS_HOST, BUS_PORT))
    
    threading.Thread(target=recv_loop, args=(sock,), daemon=True).start()
    destino = 'CLI01'  # Cambia por el nombre del servicio al que quieres enviar mensajes
    send_loop(sock,destino)


if __name__ == "__main__":
    main()