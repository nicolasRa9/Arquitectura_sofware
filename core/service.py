import socket
from typing import Callable

from common.soa_formatter import soa_formatter
from common.services_mapping import services_mapping


def _recv_exact(sock: socket.socket, n: int) -> bytes:
    """Recibe exactamente *n* bytes o corta si la conexión se pierde."""
    data = b""
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            break
        data += packet
    return data


class Service:
    """Clase base para un microservicio SOA sobre sockets TCP."""

    def __init__(self, service_name: str, host: str, port: int) -> None:
        if service_name not in services_mapping:
            raise ValueError(f"Service name '{service_name}' is not in services_mapping.")
        self.service_name = service_name
        self.host, self.port = host, port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(1.0)

    # ---------- helpers ----------
    def _init_service(self) -> None:
        handshake = f"00010sinit{services_mapping[self.service_name]}"
        self.sock.sendall(handshake.encode())

    def _send_response(self, data: str) -> None:
        payload = soa_formatter(self.service_name, data)
        if payload:
            self.sock.sendall(payload)

    # ---------- API ----------
    def run_service(self, service_func: Callable[[str], str]):
        """Escucha mensajes para este servicio y responde usando *service_func*."""
        try:
            with self.sock as s:
                s.connect((self.host, self.port))
                print(f"[{self.service_name}] Conectado a {self.host}:{self.port}")
                self._init_service()

                init_done = False

                while True:
                    try:
                        header = s.recv(10)
                    except socket.timeout:
                        continue  # permite Ctrl+C sin bloquear

                    if not header:
                        continue

                    header_dec = header.decode()
                    length = int(header_dec[:5])
                    service_code = header_dec[5:10].strip()

                    body = _recv_exact(s, length - 5).decode()

                    if not init_done:
                        init_done = True
                        print(f"[{self.service_name}] Handshake recibido.")
                        continue

                    if service_code == services_mapping[self.service_name]:
                        try:
                            reply = service_func(body)
                        except Exception as e:
                            reply = f"ERROR: {e}"
                        self._send_response(reply)
                        print(f"[{self.service_name}] Respuesta enviada: {reply}")
                    else:
                        print(f"[{self.service_name}] Mensaje para otro servicio ({service_code}).")
        except Exception as exc:
            print(f"[{self.service_name}] ERROR: {exc}")
        finally:
            print(f"[{self.service_name}] Servicio apagado.")
