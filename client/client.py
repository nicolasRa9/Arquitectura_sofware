import socket, time

def construir_transaccion(servicio, datos):
    servicio = servicio.ljust(5)  # Asegura que tenga largo 5
    contenido = servicio + datos
    longitud = str(len(contenido)).zfill(5)
    return longitud + contenido

def enviar_transaccion(mensaje):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('bus', 5000))
    try:
        sock.sendall(mensaje.encode())
        respuesta = sock.recv(1024).decode()
        print("Respuesta del bus:", respuesta)
    finally:
        sock.close()

time.sleep(10)

# Ejemplo de uso
datos = "120 345"
mensaje = construir_transaccion("sum01", datos)
enviar_transaccion(mensaje)