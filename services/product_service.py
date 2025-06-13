
from __future__ import annotations

from core import Service
from database import insert_producto


def register_product(data: str) -> str:
    """
    Espera pares clave=valor separados por ';', p. ej.:
        "id=123;name=Box;size=2x2;weight=10"
    """
    try:
        parts = dict(item.split("=", 1) for item in data.split(";"))
        product_id = parts.get("id")
        name = parts.get("name")
        size = parts.get("size")
        weight = float(parts["weight"]) if parts.get("weight") else None

        insert_producto(product_id, name, size, weight)
        print(f"[PRODUCT_MANAGER] Registrado {product_id}: {name} ({size}, {weight}kg)")
        return "OK: Producto registrado"
    except Exception as exc:
        return f"ERROR: {exc}"


if __name__ == "__main__":
    Service("product_manager", "localhost", 9100).run_service(register_product)
