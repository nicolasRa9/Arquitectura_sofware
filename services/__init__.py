"""
Colección de microservicios SOA para el WMS.
"""

__all__ = [
    "product_service",
    "optimizer_service",
    "movement_service",
    "visualizer_service",
    "report_service",
]

from . import (  # noqa: F401
    product_service,
    optimizer_service,
    movement_service,
    visualizer_service,
    report_service,
)
