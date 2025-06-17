#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servicio de Ubicaciones - RF-2
Maneja la gestión de ubicaciones, estantes y zonas en el sistema WMS
"""
import socket
import sys
import json
import psycopg2
import os
from datetime import datetime
from time import sleep

class LocationService:
    def __init__(self):
        self.bus_address = ('localhost', 5000)
        self.service_name = 'location_service'
        self.db_config = {
            'host': os.getenv('DB_HOST', 'db'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres'),
            'database': os.getenv('DB_NAME', 'wms')
        }
        
    def connect_db(self):
        """Conecta a la base de datos PostgreSQL"""
        try:
            return psycopg2.connect(**self.db_config)
        except Exception as e:
            print(f"Error conectando a la base de datos: {e}")
            return None
    
    def create_location(self, data):
        """Crear una nueva ubicación"""
        try:
            conn = self.connect_db()
            if not conn:
                return {"error": "No se pudo conectar a la base de datos"}
            
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO ubicacion (codigo, nombre, capacidad, zona, estante, tipo)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id_ubicacion
                """, (
                    data.get('codigo'),
                    data.get('nombre', ''),
                    data.get('capacidad'),
                    data.get('zona', ''),
                    data.get('estante', ''),
                    data.get('tipo', 'Almacenamiento')
                ))
                
                location_id = cur.fetchone()[0]
                conn.commit()
                
                return {
                    "success": True,
                    "message": "Ubicación creada exitosamente",
                    "id_ubicacion": location_id
                }
                
        except Exception as e:
            return {"error": f"Error creando ubicación: {str(e)}"}
        finally:
            if conn:
                conn.close()
    
    def get_locations(self):
        """Obtener todas las ubicaciones"""
        try:
            conn = self.connect_db()
            if not conn:
                return {"error": "No se pudo conectar a la base de datos"}
            
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id_ubicacion, codigo, nombre, capacidad, zona, estante, tipo, fecha_creacion
                    FROM ubicacion
                    ORDER BY codigo
                """)
                
                locations = []
                for row in cur.fetchall():
                    locations.append({
                        "id_ubicacion": row[0],
                        "codigo": row[1],
                        "nombre": row[2],
                        "capacidad": float(row[3]),
                        "zona": row[4],
                        "estante": row[5],
                        "tipo": row[6],
                        "fecha_creacion": row[7].isoformat() if row[7] else None
                    })
                
                return {
                    "success": True,
                    "locations": locations,
                    "count": len(locations)
                }
                
        except Exception as e:
            return {"error": f"Error obteniendo ubicaciones: {str(e)}"}
        finally:
            if conn:
                conn.close()
    
    def get_location(self, location_id):
        """Obtener una ubicación específica"""
        try:
            conn = self.connect_db()
            if not conn:
                return {"error": "No se pudo conectar a la base de datos"}
            
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id_ubicacion, codigo, nombre, capacidad, zona, estante, tipo, fecha_creacion
                    FROM ubicacion
                    WHERE id_ubicacion = %s
                """, (location_id,))
                
                row = cur.fetchone()
                if row:
                    return {
                        "success": True,
                        "location": {
                            "id_ubicacion": row[0],
                            "codigo": row[1],
                            "nombre": row[2],
                            "capacidad": float(row[3]),
                            "zona": row[4],
                            "estante": row[5],
                            "tipo": row[6],
                            "fecha_creacion": row[7].isoformat() if row[7] else None
                        }
                    }
                else:
                    return {"error": "Ubicación no encontrada"}
                
        except Exception as e:
            return {"error": f"Error obteniendo ubicación: {str(e)}"}
        finally:
            if conn:
                conn.close()
    
    def get_locations_by_zone(self, zone):
        """Obtener ubicaciones por zona"""
        try:
            conn = self.connect_db()
            if not conn:
                return {"error": "No se pudo conectar a la base de datos"}
            
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id_ubicacion, codigo, nombre, capacidad, zona, estante, tipo
                    FROM ubicacion
                    WHERE zona = %s
                    ORDER BY codigo
                """, (zone,))
                
                locations = []
                for row in cur.fetchall():
                    locations.append({
                        "id_ubicacion": row[0],
                        "codigo": row[1],
                        "nombre": row[2],
                        "capacidad": float(row[3]),
                        "zona": row[4],
                        "estante": row[5],
                        "tipo": row[6]
                    })
                
                return {
                    "success": True,
                    "locations": locations,
                    "zone": zone,
                    "count": len(locations)
                }
                
        except Exception as e:
            return {"error": f"Error obteniendo ubicaciones por zona: {str(e)}"}
        finally:
            if conn:
                conn.close()
    
    def update_location(self, location_id, data):
        """Actualizar una ubicación"""
        try:
            conn = self.connect_db()
            if not conn:
                return {"error": "No se pudo conectar a la base de datos"}
            
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE ubicacion 
                    SET codigo = %s, nombre = %s, capacidad = %s, zona = %s, estante = %s, tipo = %s
                    WHERE id_ubicacion = %s
                """, (
                    data.get('codigo'),
                    data.get('nombre'),
                    data.get('capacidad'),
                    data.get('zona'),
                    data.get('estante'),
                    data.get('tipo'),
                    location_id
                ))
                
                if cur.rowcount == 0:
                    return {"error": "Ubicación no encontrada"}
                
                conn.commit()
                return {
                    "success": True,
                    "message": "Ubicación actualizada exitosamente"
                }
                
        except Exception as e:
            return {"error": f"Error actualizando ubicación: {str(e)}"}
        finally:
            if conn:
                conn.close()
    
    def delete_location(self, location_id):
        """Eliminar una ubicación"""
        try:
            conn = self.connect_db()
            if not conn:
                return {"error": "No se pudo conectar a la base de datos"}
            
            with conn.cursor() as cur:
                cur.execute("DELETE FROM ubicacion WHERE id_ubicacion = %s", (location_id,))
                
                if cur.rowcount == 0:
                    return {"error": "Ubicación no encontrada"}
                
                conn.commit()
                return {
                    "success": True,
                    "message": "Ubicación eliminada exitosamente"
                }
                
        except Exception as e:
            return {"error": f"Error eliminando ubicación: {str(e)}"}
        finally:
            if conn:
                conn.close()
    
    def process_request(self, request_data):
        """Procesa las solicitudes del bus"""
        try:
            request = json.loads(request_data)
            action = request.get('action')
            
            if action == 'create':
                return self.create_location(request.get('location', {}))
            elif action == 'list':
                return self.get_locations()
            elif action == 'get':
                return self.get_location(request.get('id'))
            elif action == 'get_by_zone':
                return self.get_locations_by_zone(request.get('zone'))
            elif action == 'update':
                return self.update_location(request.get('id'), request.get('location', {}))
            elif action == 'delete':
                return self.delete_location(request.get('id'))
            else:
                return {"error": f"Acción no reconocida: {action}"}
                
        except json.JSONDecodeError:
            return {"error": "JSON inválido en la solicitud"}
        except Exception as e:
            return {"error": f"Error procesando solicitud: {str(e)}"}
    
    def run(self):
        """Ejecuta el servicio"""
        print(f"Conectando al bus en {self.bus_address}")
        
        # Crear socket y conectar al bus
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self.bus_address)
        
        try:
            # Registrar el servicio

            message = b'00010sinitservi'
            print('sending {!r}'.format(message))
            sock.sendall(message)
            sinit = 1
            
            while True:
                # Look for the response
                print("Waiting for transaction")
                amount_received = 0
                amount_expected = int(sock.recv(5))
                
                while amount_received < amount_expected:
                    data = sock.recv(amount_expected - amount_received)
                    amount_received += len(data)
                
                print('received {!r}'.format(data))
                
                if (sinit == 1):
                    sinit = 0
                    print('Received sinit answer')
                else:
                    # Procesar la solicitud
                    try:
                        response = self.process_request(data.decode())
                        response_json = json.dumps(response, ensure_ascii=False)
                        
                        # Enviar respuesta
                        response_message = f'{len(response_json):05}{response_json}'.encode()
                        print(f'Enviando respuesta: {response_message}')
                        sock.sendall(response_message)
                        
                    except Exception as e:
                        error_response = {"error": f"Error interno: {str(e)}"}
                        error_json = json.dumps(error_response, ensure_ascii=False)
                        error_message = f'{len(error_json):05}{error_json}'.encode()
                        sock.sendall(error_message)
                
        except KeyboardInterrupt:
            print("Servicio detenido por el usuario")
        except Exception as e:
            print(f"Error en el servicio: {e}")
        finally:
            print('Cerrando socket')
            sock.close()

if __name__ == "__main__":
    service = LocationService()
    service.run() 