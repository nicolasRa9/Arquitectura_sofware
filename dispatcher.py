from __future__ import annotations

import socket
import threading
from typing import Dict

HOST = "0.0.0.0"
PORT = 9100
BUFFER = 4096

# Sockets registrados por código de servicio (SV001…)
services: Dict[str, socket.socket] = {}
lock = threading.Lock()

def _recv_exact(sock: socket.socket, n: int) -> bytes:
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            break
        data += chunk
    return data


def _pipe(src: socket.socket, dst: socket.socket):
    try:
        while True:
            data = src.recv(BUFFER)
            if not data:
                break
            dst.sendall(data)
    finally:
        src.close()
        dst.close()


def handle_connection(sock: socket.socket, addr):
    try:
        header = _recv_exact(sock, 10)
        if not header:
            sock.close()
            return
        length = int(header[:5].decode())
        tag = header[5:10].decode()
        body = _recv_exact(sock, length - 5)
        code = body.decode().strip()

        if tag != "sinit" or not code.startswith("SV"):
            sock.sendall(b"ERROR: Invalid handshake")
            sock.close()
            return

        # ----- Registro de microservicio o cliente -----
        with lock:
            if code not in services:
                # Primer socket con este código se asume microservicio
                services[code] = sock
                print(f"[REG] Microservicio {code} registrado desde {addr}")
                return  # microservicio queda esperando mensajes
            else:
                # Cliente quiere hablar con servicio ya registrado
                service_sock = services[code]

        print(f"[TUNNEL] Cliente {addr} ↔ {code}")
        # Reenviar handshake al microservicio
        service_sock.sendall(header + body)

        # Crear túnel bidireccional
        threading.Thread(target=_pipe, args=(sock, service_sock), daemon=True).start()
        _pipe(service_sock, sock)
    except Exception as exc:
        try:
            sock.sendall(f"ERROR: {exc}".encode())
        except Exception:
            pass
        sock.close()
    finally:
        print(f"Conexión finalizada {addr}")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"Dispatcher escuchando en {HOST}:{PORT}")
        while True:
            s, addr = server.accept()
            threading.Thread(target=handle_connection, args=(s, addr), daemon=True).start()


if __name__ == "__main__":
    main()
