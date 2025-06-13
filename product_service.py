from __future__ import annotations

import os
from .core import Service
from .database import insert_producto


def register_product(data: str) -> str:
    """
    Registra un producto en la base de datos.
    Espera pares clave=valor separados por ';', p. ej.:
        "id=123;name=Box;size=2x2;weight=10"
    """
    try:
        parts = dict(item.split("=", 1) for item in data.split(";"))
        product_id = parts.get("id")
        name = parts.get("name")
        size = parts.get("size")
        weight = float(parts["weight"]) if parts.get("weight") else None

        if not product_id or not name:
            return "ERROR: ID y nombre son requeridos"

        insert_producto(product_id, name, size, weight)
        print(f"[PRODUCT_MANAGER] Registrado {product_id}: {name} ({size}, {weight}kg)")
        return f"OK: Producto {product_id} registrado exitosamente"
    except ValueError as e:
        return f"ERROR: Formato de peso inválido - {e}"
    except Exception as exc:
        return f"ERROR: {exc}"


if __name__ == "__main__":
    # Usar variables de entorno del docker-compose
    bus_host = os.getenv('BUS_HOST', 'localhost')
    bus_port = int(os.getenv('BUS_PORT', 9100))
    
    print(f"[PRODUCT_SERVICE] Iniciando servicio...")
    print(f"[PRODUCT_SERVICE] Bus SOA: {bus_host}:{bus_port}")
    
    service = Service("product_manager", bus_host, bus_port)
    service.run_service(register_product)