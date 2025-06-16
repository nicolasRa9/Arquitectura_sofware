def construir_mensaje_bus(servicio: str, datos: str) -> str:
    """
    Construye un mensaje con el formato del bus:
    NNNNNSSSSSDATOS
    
    - NNNNN: Largo total de SSSSS + DATOS
    - SSSSS: Nombre del servicio (exactamente 5 caracteres, se rellena con espacios si es más corto)
    - DATOS: Cualquier cadena de datos

    :param servicio: Nombre del servicio (ej. "sumar")
    :param datos: Cadena de datos (ej. "120 345")
    :return: Mensaje completo para enviar al bus
    """
    servicio_formateado = servicio.ljust(5)[:5]  # Asegura largo 5, recorta si es mayor
    cuerpo = servicio_formateado + datos
    longitud = str(len(cuerpo)).zfill(5)
    return longitud + cuerpo