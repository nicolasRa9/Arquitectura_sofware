import socket

def send_message(host, port, messages):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        for msg in messages:
            s.sendall(msg.encode())
            response = s.recv(1024)
            print(">> Respuesta:", response.decode())

if __name__ == "__main__":
    # simular inicialización y envío de datos a product_manager
    send_message("localhost", 9001, [
        "00010sinitSV001",
        "00044SV001id=123;name=Box;size=2x2"
    ])