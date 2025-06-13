from __future__ import annotations

import os
import socket
import sys
import time
from typing import List

from common import soa_formatter, services_mapping


def send_message(host: str, port: int, messages: List[str]):
    """Envía mensajes al bus SOA con manejo de errores mejorado."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10.0)  # Timeout de 10 segundos
            print(f"Conectando al bus SOA en {host}:{port}...")
            s.connect((host, port))
            print("Conexión establecida")
            
            for i, msg in enumerate(messages, 1):
                print(f"=> Enviando mensaje {i}/{len(messages)}: {msg!r}")
                s.sendall(msg.encode())
                
                try:
                    response = s.recv(4096)  # Buffer más grande
                    if response:
                        print(f"<= Respuesta {i}: {response.decode()}")
                    else:
                        print(f"<= Sin respuesta para mensaje {i}")
                except socket.timeout:
                    print(f"<= Timeout esperando respuesta {i}")
                
                # Pequeña pausa entre mensajes
                if i < len(messages):
                    time.sleep(0.5)
                    
    except ConnectionRefusedError:
        print(f"ERROR: No se pudo conectar a {host}:{port}. ¿Está el bus SOA funcionando?")
    except socket.timeout:
        print("ERROR: Timeout de conexión")
    except Exception as e:
        print(f"ERROR: {e}")


def main():
    if len(sys.argv) < 3:
        print("Uso: python -m client.test_client <service_name> <data_string> [host] [port]")
        print("\nServicios disponibles:")
        for service, code in services_mapping.items():
            print(f"  - {service} ({code})")
        sys.exit(1)

    service_name = sys.argv[1]
    data_str = sys.argv[2]
    
    # Usar variables de entorno o argumentos de línea de comandos
    host = sys.argv[3] if len(sys.argv) > 3 else os.getenv('BUS_HOST', 'localhost')
    port = int(sys.argv[4]) if len(sys.argv) > 4 else int(os.getenv('BUS_PORT', 9100))

    if service_name not in services_mapping:
        print(f"ERROR: '{service_name}' no está en services_mapping")
        print("Servicios disponibles:")
        for service, code in services_mapping.items():
            print(f"  - {service} ({code})")
        sys.exit(1)

    print(f"Cliente SOA iniciado")
    print(f"Servicio objetivo: {service_name} ({services_mapping[service_name]})")
    print(f"Datos: {data_str}")
    print(f"Bus SOA: {host}:{port}")
    print("-" * 50)

    # Preparar mensajes
    sinit = "00010sinit" + services_mapping[service_name]
    formatted = soa_formatter(service_name, data_str)
    
    if formatted is None:
        print("ERROR: No se pudo formatear el mensaje")
        sys.exit(1)
    
    formatted_str = formatted.decode()

    messages = [sinit, formatted_str]
    
    print("Mensajes a enviar:")
    for i, msg in enumerate(messages, 1):
        print(f"  {i}. {msg}")
    print("-" * 50)

    send_message(host, port, messages)


if __name__ == "__main__":
    main()