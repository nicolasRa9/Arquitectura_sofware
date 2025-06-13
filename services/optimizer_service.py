
from __future__ import annotations

from core import Service


def suggest_location(data: str) -> str:
    """Expects: 'size=2x2;weight=10;demand=high'."""
    try:
        parts = dict(item.split("=", 1) for item in data.split(";"))
        demand = parts.get("demand", "low")
        return "Ubicación sugerida: A1-Z3" if demand == "high" else "Ubicación sugerida: B4-X2"
    except Exception as exc:
        return f"ERROR: {exc}"


if __name__ == "__main__":
    Service("location_optimizer", "localhost", 9002).run_service(suggest_location)
