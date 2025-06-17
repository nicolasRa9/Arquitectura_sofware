#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente de prueba para el sistema WMS
Permite interactuar con todos los servicios del sistema
"""

import socket
import json
import sys
import argparse

class WMSClient:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.bus_address = (host, port)
    
    def send_request(self, service_name, request_data):
        """Envía una solicitud al servicio especificado"""
        try:
            # Crear socket y conectar al bus
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(self.bus_address)
            
            # Preparar el mensaje
            message = json.dumps(request_data)
            service_message = f'{len(message):05}{service_name}{message}'.encode()
            
            print(f"Enviando a {service_name}: {message}")
            sock.sendall(service_message)
            
            # Recibir respuesta
            amount_received = 0
            amount_expected = int(sock.recv(5))
            
            data = b''
            while amount_received < amount_expected:
                chunk = sock.recv(amount_expected - amount_received)
                if not chunk:
                    break
                data += chunk
                amount_received += len(chunk)
            
            response = json.loads(data.decode())
            sock.close()
            
            return response
            
        except Exception as e:
            return {"error": f"Error de comunicación: {str(e)}"}
    
    def test_product_service(self):
        """Prueba el servicio de productos"""
        print("\n=== Prueba del Servicio de Productos ===")
        
        # Listar productos
        print("\n1. Listando productos...")
        response = self.send_request('product_service', {"action": "list"})
        print(f"Respuesta: {json.dumps(response, indent=2, ensure_ascii=False)}")
        
        # Crear un producto
        print("\n2. Creando un producto...")
        product_data = {
            "nombre": "Laptop Dell Inspiron",
            "descripcion": "Laptop de 14 pulgadas con procesador Intel i5",
            "tamanio": 14.0,
            "peso": 1.8,
            "categoria": "Electrónicos",
            "rotacion": "Alta"
        }
        response = self.send_request('product_service', {
            "action": "create",
            "product": product_data
        })
        print(f"Respuesta: {json.dumps(response, indent=2, ensure_ascii=False)}")
        
        # Listar productos nuevamente
        print("\n3. Listando productos después de crear...")
        response = self.send_request('product_service', {"action": "list"})
        print(f"Respuesta: {json.dumps(response, indent=2, ensure_ascii=False)}")
    
    def test_location_service(self):
        """Prueba el servicio de ubicaciones"""
        print("\n=== Prueba del Servicio de Ubicaciones ===")
        
        # Listar ubicaciones
        print("\n1. Listando ubicaciones...")
        response = self.send_request('location_service', {"action": "list"})
        print(f"Respuesta: {json.dumps(response, indent=2, ensure_ascii=False)}")
        
        # Crear una ubicación
        print("\n2. Creando una ubicación...")
        location_data = {
            "codigo": "C1-B1-C1",
            "nombre": "Pasillo C, Estante 1, Nivel 1",
            "capacidad": 120.0,
            "zona": "C",
            "estante": "B1",
            "tipo": "Almacenamiento"
        }
        response = self.send_request('location_service', {
            "action": "create",
            "location": location_data
        })
        print(f"Respuesta: {json.dumps(response, indent=2, ensure_ascii=False)}")
        
        # Listar ubicaciones por zona
        print("\n3. Listando ubicaciones de la zona A...")
        response = self.send_request('location_service', {
            "action": "get_by_zone",
            "zone": "A"
        })
        print(f"Respuesta: {json.dumps(response, indent=2, ensure_ascii=False)}")
    
    def test_all_services(self):
        """Prueba todos los servicios"""
        print("Iniciando pruebas de todos los servicios...")
        
        # Probar servicio de productos
        self.test_product_service()
        
        # Probar servicio de ubicaciones
        self.test_location_service()
        
        print("\n=== Pruebas completadas ===")

def main():
    parser = argparse.ArgumentParser(description='Cliente de prueba para el sistema WMS')
    parser.add_argument('--host', default='localhost', help='Host del bus de servicios')
    parser.add_argument('--port', type=int, default=5000, help='Puerto del bus de servicios')
    parser.add_argument('--service', choices=['product', 'location', 'all'], default='all',
                       help='Servicio a probar')
    
    args = parser.parse_args()
    
    client = WMSClient(args.host, args.port)
    
    if args.service == 'product':
        client.test_product_service()
    elif args.service == 'location':
        client.test_location_service()
    else:
        client.test_all_services()

if __name__ == "__main__":
    main() 