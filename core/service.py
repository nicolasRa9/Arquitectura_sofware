import os
import socket
import time
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
    """Clase base para un microservicio SOA que se conecta al bus jrgiadach/soabus:v1."""

    def __init__(self, service_name: str, host: str = None, port: int = None) -> None:
        if service_name not in services_mapping:
            raise ValueError(f"Service name '{service_name}' is not in services_mapping.")
        
        self.service_name = service_name
        # Usar variables de entorno si están disponibles
        self.host = host or os.getenv('BUS_HOST', 'localhost')
        self.port = port or int(os.getenv('BUS_PORT', 9100))
        self.service_code = services_mapping[service_name]
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(5.0)  # Timeout más largo para el bus

    def _connect_with_retry(self, max_retries: int = 5) -> bool:
        """Intenta conectar al bus con reintentos."""
        for attempt in range(max_retries):
            try:
                print(f"[{self.service_name}] Intento de conexión {attempt + 1}/{max_retries} a {self.host}:{self.port}")
                self.sock.connect((self.host, self.port))
                return True
            except (ConnectionRefusedError, socket.timeout) as e:
                print(f"[{self.service_name}] Error de conexión: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Backoff exponencial
                else:
                    print(f"[{self.service_name}] No se pudo conectar después de {max_retries} intentos")
                    return False
        return False

    def _init_service(self) -> None:
        """Registra el servicio en el bus SOA."""
        handshake = f"00010sinit{self.service_code}"
        print(f"[{self.service_name}] Enviando handshake: {handshake}")
        self.sock.sendall(handshake.encode())
        
        # Esperar confirmación del bus (si es necesario)
        try:
            response = self.sock.recv(1024)
            if response:
                print(f"[{self.service_name}] Respuesta del bus: {response.decode()}")
        except socket.timeout:
            print(f"[{self.service_name}] No hay respuesta del bus (puede ser normal)")

    def _send_response(self, data: str) -> None:
        """Envía respuesta usando el formateador SOA."""
        payload = soa_formatter(self.service_name, data)
        if payload:
            self.sock.sendall(payload)
            print(f"[{self.service_name}] Respuesta enviada: {len(payload)} bytes")

    def run_service(self, service_func: Callable[[str], str]):
        """Escucha mensajes del bus y responde usando *service_func*."""
        try:
            # Conectar con reintentos
            if not self._connect_with_retry():
                print(f"[{self.service_name}] Error fatal: No se pudo conectar al bus")
                return

            print(f"[{self.service_name}] Conectado al bus SOA en {self.host}:{self.port}")
            
            # Registrar servicio
            self._init_service()
            print(f"[{self.service_name}] Servicio registrado con código {self.service_code}")

            init_done = False
            message_count = 0

            while True:
                try:
                    # Recibir header (10 bytes: 5 length + 5 service code)
                    header = self.sock.recv(10)
                    if not header:
                        print(f"[{self.service_name}] Conexión cerrada por el bus")
                        break

                    if len(header) < 10:
                        print(f"[{self.service_name}] Header incompleto: {len(header)} bytes")
                        continue

                    header_str = header.decode()
                    length = int(header_str[:5])
                    service_code = header_str[5:10].strip()

                    print(f"[{self.service_name}] Mensaje recibido - Length: {length}, Code: {service_code}")

                    # Recibir el cuerpo del mensaje
                    body = _recv_exact(self.sock, length - 5).decode()

                    # Manejar confirmación inicial
                    if not init_done:
                        init_done = True
                        print(f"[{self.service_name}] Handshake confirmado por el bus")
                        continue

                    # Procesar mensaje si es para este servicio
                    if service_code == self.service_code:
                        message_count += 1
                        print(f"[{self.service_name}] Procesando mensaje #{message_count}: {body}")
                        
                        try:
                            reply = service_func(body)
                            print(f"[{self.service_name}] Respuesta generada: {reply}")
                        except Exception as e:
                            reply = f"ERROR: {e}"
                            print(f"[{self.service_name}] Error en función de servicio: {e}")
                        
                        self._send_response(reply)
                    else:
                        print(f"[{self.service_name}] Mensaje ignorado (código {service_code} != {self.service_code})")

                except socket.timeout:
                    # Timeout normal, continuar
                    continue
                except Exception as e:
                    print(f"[{self.service_name}] Error procesando mensaje: {e}")
                    continue

        except KeyboardInterrupt:
            print(f"[{self.service_name}] Interrupción por teclado")
        except Exception as exc:
            print(f"[{self.service_name}] ERROR FATAL: {exc}")
        finally:
            try:
                self.sock.close()
            except:
                pass
            print(f"[{self.service_name}] Servicio apagado. Mensajes procesados: {message_count}")