from __future__ import annotations

from core import Service


def show_warehouse(_data: str) -> str:
    """Devuelve un mapa ASCII simple del almacén."""
    ascii_map = (
        "+-------+\n"
        "| A1 A2 |\n"
        "| B1 B2 |\n"
        "+-------+"
    )
    return ascii_map


if __name__ == "__main__":
    service = Service("warehouse_visualizer", "localhost", 9004)
    service.run_service(show_warehouse)
