import os

def construir_transaccion(servicio, datos):
    servicio = servicio.ljust(5)  # 5 caracteres
    contenido = servicio + datos
    longitud = str(len(contenido)).zfill(5)
    return longitud + contenido

def procesar_mensaje(data, service_name):
    if len(data) < 10:
        print("error <10")
        return None  # Mensaje inválido
    servicio_destino = data[5:10].strip()
    datos = data[10:]
    if servicio_destino == service_name.strip():
        print("error mach")
        return datos
    return None

def procesar_destino(data, service_name):
    if len(data) < 10:
        return None  # Mensaje inválido
    servicio_destino = data[5:10].strip()
    datos = data[10:]
    if servicio_destino == service_name.strip():
        return servicio_destino
    return None


