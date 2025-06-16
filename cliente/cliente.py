import socket
from base_clientes.leer_bus import construir_transaccion, procesar_mensaje

def main():
    host = 'localhost'  # Cambia esto si el bus está en otra máquina
    port = 5000         # Puerto del bus
    CLIENT_NAME = 'CLI01'  # Nombre del cliente
    MSG_SIZE = 1024

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            print(f'Conectado al bus en {host}:{port}')
            # Enviar mensaje de prueba de 10 bytes
            
            data = 'Dame la ubicacion del paquete de la mama del seba'
            Servicio_destino = 'SEV02'
            mensaje_bus = construir_transaccion(Servicio_destino,data)
            s.sendall(mensaje_bus.encode())
            print(f'Mensaje de prueba enviado: {mensaje_bus}')
            # Esperar respuesta
            data = s.recv(MSG_SIZE)
            if data:
                respuesta = data.decode()
                data = procesar_mensaje(respuesta, CLIENT_NAME)
                if data != None:
                    print(f'Respuesta procesada para el user {CLIENT_NAME}: {data}')
                else :
                    print(f'No es el cliente destino. {data}')
            else:
                print('No se recibió respuesta del bus.')
                    
        except ConnectionRefusedError:
            print("No se pudo conectar al bus.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()