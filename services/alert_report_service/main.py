import os, socket, threading, time, random, string

BUS_HOST = os.getenv("BUS_HOST", "bus_service")
BUS_PORT = int(os.getenv("BUS_PORT", "5000"))
SERVICE_NAME = os.getenv("SERVICE_NAME", "SEV01")  # Cambia por el nombre de tu servicio
MSG_SIZE = 1024 # Tamaño del mensaje que se espera recibir

def construir_transaccion(servicio, datos):
    servicio = servicio.ljust(5)  # 5 caracteres
    contenido = servicio + datos
    longitud = str(len(contenido)).zfill(5)
    return longitud + contenido

def recv_loop(sock):
    while True:
        data = sock.recv(MSG_SIZE)
        if not data:
            break
        print(f"[{SERVICE_NAME}] <- {data.decode()}")

def send_loop(sock):
    while True:
        # Ejemplo de datos: random string de 10 caracteres
        datos = ''.join(random.choices(string.ascii_uppercase, k=10))
        mensaje = construir_transaccion(SERVICE_NAME, datos)
        sock.sendall(mensaje.encode())
        print(f"[{SERVICE_NAME}] -> {mensaje}")
        time.sleep(5)

def main():
    time.sleep(2)  # Espera a que el bus esté listo
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((BUS_HOST, BUS_PORT))
    # Envía el nombre del servicio al conectar
    
    print(f"[{SERVICE_NAME}] Registrado en el bus.")

    threading.Thread(target=recv_loop, args=(sock,), daemon=True).start()
    send_loop(sock)

if __name__ == "__main__":
    main()
