from service import Service

# lógica del servicio de registro de productos
def register_product(data):
    # Supongamos que data viene como "id=123;name=Box;size=2x2"
    try:
        parts = dict(kv.split("=") for kv in data.split(";"))
        product_id = parts.get("id")
        name = parts.get("name")
        size = parts.get("size")
        print(f"Producto registrado: {product_id} - {name} - {size}")
        return "Registro exitoso"
    except Exception as e:
        return f"ERROR: {str(e)}"

if __name__ == "__main__":
    svc = Service("product_manager", "localhost", 9001)
    svc.run_service(register_product)
