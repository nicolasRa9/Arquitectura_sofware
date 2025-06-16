import os, socket, time

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

def main():
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"[{SERVICE_NAME}] Intentando conectar al bus en {BUS_HOST}:{BUS_PORT}...")
            sock.connect((BUS_HOST, BUS_PORT))
            conectado ="Conectado al bus. Esperando mensajes..."
            Servicio_destino = 'CLI02'
            mensaje_bus = construir_transaccion(Servicio_destino,conectado)
            sock.sendall(mensaje_bus.encode())
            print(f"[{SERVICE_NAME}] Conectado al bus. Esperando mensajes...")
            break
        except Exception as e:
            print(f"[{SERVICE_NAME}] No se pudo conectar al bus: {e}. Reintentando en 3s...")
            no_conectado ="Conectado al bus. Esperando mensajes..."
            Servicio_destino = 'CLI02'
            mensaje_bus = construir_transaccion(Servicio_destino,no_conectado)
            sock.sendall(mensaje_bus.encode())

    try:
        while True:
            data = sock.recv(MSG_SIZE)
            if not data:
                print(f"[{SERVICE_NAME}] Conexión cerrada por el bus. Reintentando...")
                # Intentar reconectar al bus
                no_es_data = "No es data, fallido"
                Servicio_destino = 'CLI02'
                mensaje_bus = construir_transaccion(Servicio_destino,no_es_data)
                sock.sendall(mensaje_bus.encode())
                sock.close()
                while True:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        print(f"[{SERVICE_NAME}] Intentando reconectar al bus en {BUS_HOST}:{BUS_PORT}...")
                        sock.connect((BUS_HOST, BUS_PORT))
                        print(f"[{SERVICE_NAME}] Reconectado al bus. Esperando mensajes...")
                        break
                    except Exception as e:
                        print(f"[{SERVICE_NAME}] No se pudo reconectar al bus: {e}. Reintentando ...")
                continue  # volver a escuchar mensajes

            mensaje = data.decode()
            datos = procesar_mensaje(mensaje, SERVICE_NAME)
            es_data ="es data y este es el mensaje"
            Servicio_destino = 'CLI02'

            mensaje_bus = construir_transaccion(Servicio_destino,es_data)
            sock.sendall(mensaje_bus.encode())
            if datos is None:
                datos = "No es data, fallido"
            Servicio_destino = 'CLI02'
            mensaje_bus = construir_transaccion(Servicio_destino,datos)
            sock.sendall(mensaje_bus.encode())


            if datos is not None:
                print(f"[{SERVICE_NAME}] Mensaje para mí: {datos}")
                respuesta = construir_transaccion(SERVICE_NAME, "Ubicación recibida y procesada")
                sock.sendall(respuesta.encode())
            else:
                print(f"[{SERVICE_NAME}] Mensaje para otro servicio o inválido.")
                # Sigue escuchando, no cierra la conexión
    except Exception as e:
        print(f"[{SERVICE_NAME}] Error en la conexión: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    time.sleep(2) # Espera a que el bus esté listo
    main()