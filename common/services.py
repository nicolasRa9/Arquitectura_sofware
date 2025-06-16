import socket
from .soa_formatter import soa_formatter
from .services_mapping import services_mapping

class Service:
    def __init__(self, service_name: str, host: str, port: int) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host, self.port = host, port
        self.service_name = service_name

    def _init_service(self):
        data = f"00010sinit{services_mapping[self.service_name]}"
        self.sock.sendall(data.encode())

    def _send_data(self, data: str):
        formatted_data = soa_formatter(self.service_name, data)
        self.sock.sendall(formatted_data)
    
    def run_service(self, service_func):
        try:
            with self.sock as s:
                s.connect((self.host, self.port))
                print(f"Service '{self.service_name}' listening on {self.host}:{self.port}")
                self._init_service()

                service_is_init = False

                while True:
                    header = s.recv(10).decode()
                    
                    if not header:
                        continue

                    length = int(header[:5])
                    service = header[5:10].strip()

                    if not service_is_init:
                        data = s.recv(length - 5).decode()
                        service_is_init = True
                        print("Server was init...")
                        continue

                    if service == services_mapping[self.service_name]:
                        data = s.recv(length - 5).decode()
                        
                        try:
                            response = service_func(data)
                        except Exception as e:
                            response = f"{str(e)}"
                        
                        self._send_data(response)
                        print(f"Response sent: {response}")
                    else:
                        print(f"Message not for {self.service_name}...")
        except Exception as e:
            print(f"ERROR: {e}")
            s.close()
        finally:
            s.close()