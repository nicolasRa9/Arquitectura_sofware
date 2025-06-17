#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de inicio rápido para el sistema WMS
"""

import subprocess
import time
import sys
import os

def run_command(command, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completado")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ Error en {description}: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error ejecutando {description}: {e}")
        return False

def check_docker():
    """Verifica que Docker esté instalado y corriendo"""
    print("🔍 Verificando Docker...")
    try:
        result = subprocess.run("docker --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker encontrado: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker no está instalado o no está corriendo")
            return False
    except Exception as e:
        print(f"❌ Error verificando Docker: {e}")
        return False

def main():
    print("🚀 Iniciando Sistema WMS (Warehouse Management System)")
    print("=" * 60)
    
    # Verificar Docker
    if not check_docker():
        print("❌ Docker es requerido para ejecutar el sistema")
        sys.exit(1)
    
    # Detener contenedores existentes
    print("\n🛑 Deteniendo contenedores existentes...")
    run_command("docker-compose down", "Deteniendo contenedores")
    
    # Construir y levantar el sistema (solo DB y Bus)
    print("\n🏗️ Levantando base de datos y bus de servicios...")
    if not run_command("docker-compose up -d", "Levantando servicios base"):
        print("❌ Error al levantar el sistema")
        sys.exit(1)
    
    # Esperar a que los servicios se inicialicen
    print("\n⏳ Esperando que los servicios se inicialicen...")
    time.sleep(10)
    
    # Verificar estado de los servicios
    print("\n🔍 Verificando estado de los servicios...")
    run_command("docker-compose ps", "Estado de contenedores")
    
    # Mostrar logs del bus
    print("\n📋 Mostrando logs del bus de servicios...")
    run_command("docker-compose logs --tail=10 bus", "Logs del bus")
    
    print("\n" + "=" * 60)
    print("✅ Sistema WMS iniciado correctamente!")
    print("\n📋 Servicios base disponibles:")
    print("   • Base de datos PostgreSQL: localhost:5432")
    print("   • Bus de servicios: localhost:5000")
    
    print("\n🚀 Para ejecutar los servicios (en terminales separadas):")
    print("   Terminal 1 - Productos:")
    print("     python service/product_service/product_service.py")
    print("   Terminal 2 - Ubicaciones:")
    print("     python service/location_service/location_service.py")
    print("   Terminal 3 - Optimización:")
    print("     python service/optimization_service/optimization_service.py")
    print("   Terminal 4 - Movimientos:")
    print("     python service/movement_service/movement_service.py")
    print("   Terminal 5 - Visualización:")
    print("     python service/visualization_service/visualization_service.py")
    print("   Terminal 6 - Alertas y Reportes:")
    print("     python service/alert_report_service/alert_report_service.py")
    print("   Terminal 7 - Pedidos:")
    print("     python service/order_service/order_service.py")
    
    print("\n🧪 Para probar el sistema:")
    print("   python client/test_client.py")
    print("   python client/test_client.py --service product")
    print("   python client/test_client.py --service location")
    
    print("\n📊 Para ver logs en tiempo real:")
    print("   docker-compose logs -f")
    
    print("\n🛑 Para detener el sistema:")
    print("   docker-compose down")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main() 