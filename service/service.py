import socket

def procesar_datos(datos):
    try:
        a, b = map(int, datos.strip().split())
        resultado = f"{a} + {b} = {a + b}"
        return "OK", resultado
    except Exception as e:
        return "NK", f"Error: {str(e)}"

def ejecutar_servicio(nombre_servicio, puerto):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(('bus', puerto))
    servidor.listen(5)
    print(f"Servicio '{nombre_servicio}' escuchando en puerto {puerto}...")

    while True:
        conexion, addr = servidor.accept()
        with conexion:
            data = conexion.recv(1024).decode()
            if not data:
                continue

            # data = '00012sumar120 345'
            longitud = int(data[:5])
            servicio = data[5:10]
            datos = data[10:]
            if servicio == "sum01":
                print(f"Recibido servicio: {servicio}, datos: {datos}")
                estado, respuesta = procesar_datos(datos)
                contenido = f"{servicio}{estado}{respuesta}"
                longitud_respuesta = str(len(contenido)).zfill(5)
                mensaje_respuesta = longitud_respuesta + contenido

                conexion.sendall(mensaje_respuesta.encode())


#Ejemplo de uso
if __name__ == "__main__":
    ejecutar_servicio("sum01", 5000)  # O cualquier puerto donde se conecte el bus
