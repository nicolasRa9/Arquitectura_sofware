from __future__ import annotations

import socket
import sys
from typing import List

from common import soa_formatter, services_mapping


def send_message(host: str, port: int, messages: List[str]):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        for msg in messages:
            print(f"=> Enviando: {msg!r}")
            s.sendall(msg.encode())
            response = s.recv(1024)
            print("<= Respuesta:", response.decode())


def main():
    if len(sys.argv) < 3:
        print("Uso: python -m client.test_client <service_name> <data_string> [host] [port]")
        sys.exit(1)

    service_name = sys.argv[1]
    data_str = sys.argv[2]
    host = sys.argv[3] if len(sys.argv) > 3 else "localhost"
    default_ports = {
        "product_manager": 9001,
        "location_optimizer": 9002,
        "movement_tracker": 9003,
        "warehouse_visualizer": 9004,
        "alert_report_generator": 9005,
    }
    port = int(sys.argv[4]) if len(sys.argv) > 4 else default_ports.get(service_name, 9001)

    if service_name not in services_mapping:
        print(f"ERROR: '{service_name}' no está en services_mapping")
        sys.exit(1)

    sinit = "00010sinit" + services_mapping[service_name]
    formatted = soa_formatter(service_name, data_str).decode()

    send_message(host, port, [sinit, formatted])


if __name__ == "__main__":
    main()
