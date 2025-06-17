"""
Servicio de Productos - RF-1
Maneja la gestión de productos en el sistema WMS
"""

import socket
import sys
import json
import psycopg2
import os
from datetime import datetime

class ProductService:
    def __init__(self):
        self.bus_address = ('localhost', 5000)
        self.service_name = 'product_service'
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
    
    def create_product(self, data):
        """Crear un nuevo producto"""
        try:
            conn = self.connect_db()
            if not conn:
                return {"error": "No se pudo conectar a la base de datos"}
            
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO producto (nombre, descripcion, tamanio, peso, categoria, rotacion)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id_producto
                """, (
                    data.get('nombre'),
                    data.get('descripcion', ''),
                    data.get('tamanio'),
                    data.get('peso'),
                    data.get('categoria'),
                    data.get('rotacion')
                ))
                
                product_id = cur.fetchone()[0]
                conn.commit()
                
                return {
                    "success": True,
                    "message": "Producto creado exitosamente",
                    "id_producto": product_id
                }
                
        except Exception as e:
            return {"error": f"Error creando producto: {str(e)}"}
        finally:
            if conn:
                conn.close()
    
    def get_products(self):
        """Obtener todos los productos"""
        try:
            conn = self.connect_db()
            if not conn:
                return {"error": "No se pudo conectar a la base de datos"}
            
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id_producto, nombre, descripcion, tamanio, peso, categoria, rotacion, fecha_creacion
                    FROM producto
                    ORDER BY nombre
                """)
                
                products = []
                for row in cur.fetchall():
                    products.append({
                        "id_producto": row[0],
                        "nombre": row[1],
                        "descripcion": row[2],
                        "tamanio": float(row[3]),
                        "peso": float(row[4]),
                        "categoria": row[5],
                        "rotacion": row[6],
                        "fecha_creacion": row[7].isoformat() if row[7] else None
                    })
                
                return {
                    "success": True,
                    "products": products,
                    "count": len(products)
                }
                
        except Exception as e:
            return {"error": f"Error obteniendo productos: {str(e)}"}
        finally:
            if conn:
                conn.close()
    
    def get_product(self, product_id):
        """Obtener un producto específico"""
        try:
            conn = self.connect_db()
            if not conn:
                return {"error": "No se pudo conectar a la base de datos"}
            
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id_producto, nombre, descripcion, tamanio, peso, categoria, rotacion, fecha_creacion
                    FROM producto
                    WHERE id_producto = %s
                """, (product_id,))
                
                row = cur.fetchone()
                if row:
                    return {
                        "success": True,
                        "product": {
                            "id_producto": row[0],
                            "nombre": row[1],
                            "descripcion": row[2],
                            "tamanio": float(row[3]),
                            "peso": float(row[4]),
                            "categoria": row[5],
                            "rotacion": row[6],
                            "fecha_creacion": row[7].isoformat() if row[7] else None
                        }
                    }
                else:
                    return {"error": "Producto no encontrado"}
                
        except Exception as e:
            return {"error": f"Error obteniendo producto: {str(e)}"}
        finally:
            if conn:
                conn.close()
    
    def update_product(self, product_id, data):
        """Actualizar un producto"""
        try:
            conn = self.connect_db()
            if not conn:
                return {"error": "No se pudo conectar a la base de datos"}
            
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE producto 
                    SET nombre = %s, descripcion = %s, tamanio = %s, peso = %s, categoria = %s, rotacion = %s
                    WHERE id_producto = %s
                """, (
                    data.get('nombre'),
                    data.get('descripcion'),
                    data.get('tamanio'),
                    data.get('peso'),
                    data.get('categoria'),
                    data.get('rotacion'),
                    product_id
                ))
                
                if cur.rowcount == 0:
                    return {"error": "Producto no encontrado"}
                
                conn.commit()
                return {
                    "success": True,
                    "message": "Producto actualizado exitosamente"
                }
                
        except Exception as e:
            return {"error": f"Error actualizando producto: {str(e)}"}
        finally:
            if conn:
                conn.close()
    
    def delete_product(self, product_id):
        """Eliminar un producto"""
        try:
            conn = self.connect_db()
            if not conn:
                return {"error": "No se pudo conectar a la base de datos"}
            
            with conn.cursor() as cur:
                cur.execute("DELETE FROM producto WHERE id_producto = %s", (product_id,))
                
                if cur.rowcount == 0:
                    return {"error": "Producto no encontrado"}
                
                conn.commit()
                return {
                    "success": True,
                    "message": "Producto eliminado exitosamente"
                }
                
        except Exception as e:
            return {"error": f"Error eliminando producto: {str(e)}"}
        finally:
            if conn:
                conn.close()
    
    def process_request(self, request_data):
        """Procesa las solicitudes del bus"""
        try:
            print(f"Procesando request_data: {request_data}")
            print(f"Tipo de request_data: {type(request_data)}")
            
            request = json.loads(request_data)
            print(f"JSON parseado: {request}")
            print(f"Tipo de request: {type(request)}")
            
            action = request.get('action')
            print(f"Action extraído: {action}")
            print(f"Tipo de action: {type(action)}")
            
            if action == 'create':
                return self.create_product(request.get('product', {}))
            elif action == 'list':
                return self.get_products()
            elif action == 'get':
                return self.get_product(request.get('id'))
            elif action == 'update':
                return self.update_product(request.get('id'), request.get('product', {}))
            elif action == 'delete':
                return self.delete_product(request.get('id'))
            else:
                return {"error": f"Acción no reconocida: {action}"}
                
        except json.JSONDecodeError as e:
            print(f"Error JSON: {e}")
            print(f"Datos que causaron error: {request_data}")
            return {"error": f"JSON inválido en la solicitud: {str(e)}"}
        except Exception as e:
            print(f"Error general: {e}")
            return {"error": f"Error procesando solicitud: {str(e)}"}
    
    def run(self):
        """Ejecuta el servicio"""
        print(f"Conectando al bus en {self.bus_address}")
        
        # Crear socket y conectar al bus
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self.bus_address)
        
        try:
            # Send data - formato exacto del ejemplo
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
            print('closing socket')
            sock.close()

if __name__ == "__main__":
    service = ProductService()
    service.run() 