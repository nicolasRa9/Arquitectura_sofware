#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servicio de Alertas y Reportes - RF-8, RF-9
Maneja alertas generadas y reportes agregados
"""

import socket
import json
import psycopg2
import os

class AlertReportService:
    def __init__(self):
        self.bus_address = ('bus', 5000)
        self.service_name = 'alert_report_service'
        self.db_config = {
            'host': os.getenv('DB_HOST', 'db'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres'),
            'database': os.getenv('DB_NAME', 'wms')
        }
    
    def run(self):
        """Ejecuta el servicio"""
        print(f"Servicio de Alertas y Reportes iniciado - Conectando al bus en {self.bus_address}")
        
        # Crear socket y conectar al bus
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self.bus_address)
        
        try:
            # Registrar el servicio
            message = f'00010sinit{self.service_name}'.encode()
            print(f'Enviando registro: {message}')
            sock.sendall(message)
            
            while True:
                print("Esperando transacción...")
                
                # Recibir longitud del mensaje
                amount_received = 0
                amount_expected = int(sock.recv(5))
                
                # Recibir el mensaje completo
                data = b''
                while amount_received < amount_expected:
                    chunk = sock.recv(amount_expected - amount_received)
                    if not chunk:
                        break
                    data += chunk
                    amount_received += len(chunk)
                
                print(f'Recibido: {data}')
                
                # Respuesta placeholder
                response = {"message": "Servicio de alertas y reportes en desarrollo"}
                response_json = json.dumps(response, ensure_ascii=False)
                response_message = f'{len(response_json):05}{response_json}'.encode()
                sock.sendall(response_message)
                
        except Exception as e:
            print(f"Error en el servicio: {e}")
        finally:
            sock.close()

if __name__ == "__main__":
    service = AlertReportService()
    service.run() 