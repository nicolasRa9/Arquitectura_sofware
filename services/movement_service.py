
from __future__ import annotations

from core import Service
from database import insert_movimiento


def track_movement(data: str) -> str:
    """Expects: 'id=123;from=A1;to=B2'."""
    try:
        parts = dict(item.split("=", 1) for item in data.split(";"))
        product_id = parts.get("id")
        origin = parts.get("from")
        dest = parts.get("to")
        insert_movimiento(product_id, origin, dest)
        print(f"[MOVEMENT] {product_id}: {origin} -> {dest}")
        return "OK: Movimiento registrado"
    except Exception as exc:
        return f"ERROR: {exc}"


if __name__ == "__main__":
    Service("movement_tracker", "localhost", 9003).run_service(track_movement)
