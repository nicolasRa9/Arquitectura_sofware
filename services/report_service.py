from __future__ import annotations

from core import Service
from database import all_productos


def generate_report(_data: str) -> str:
    productos = list(all_productos())
    total = len(productos)
    return f"Reporte: {total} productos registrados."


if __name__ == "__main__":
    Service("alert_report_generator", "localhost", 9005).run_service(generate_report)
