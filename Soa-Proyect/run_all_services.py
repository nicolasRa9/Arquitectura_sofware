import subprocess
import os
import sys

# Lista de scripts de servicios SOA
services = [
    "product_service.py",
    "storage_optimization_service.py",
    "movement_control_service.py",
    "visualization_service.py",
    "alerts_reports_service.py",
    "ubicacion_service.py",
    "ordern_service.py",
    "create_almacen_service.py",
    "almacenamiento_service.py"
]

# Ejecutar todos los scripts en segundo plano
for service in services:
    if os.path.exists(service):
        subprocess.Popen([sys.executable, service])
    else:
        print(f" Archivo no encontrado: {service}")
