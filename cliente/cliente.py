import socket

def main():
    host = 'localhost'  # Cambia esto si el bus está en otra máquina
    port = 9000         # Puerto del bus
    MSG_SIZE = 10

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            print(f'Conectado al bus en {host}:{port}')
            # Enviar mensaje de prueba de 10 bytes
            test_msg = 'CLIENTEOK'.ljust(MSG_SIZE)[:MSG_SIZE].encode()
            s.sendall(test_msg)
            print(f'Mensaje de prueba enviado: {test_msg}')
            # Esperar respuesta
            data = s.recv(MSG_SIZE)
            if data:
                print('Conexión exitosa: recibido del bus:', data)
            else:
                print('No se recibió respuesta del bus.')
        except ConnectionRefusedError:
            print("No se pudo conectar al bus.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()