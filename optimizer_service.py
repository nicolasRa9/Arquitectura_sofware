from service import Service

def suggest_location(data):
    # data = "size=2x2;weight=10;demand=high"
    try:
        if "high" in data:
            return "Ubicación sugerida: A1-Z3"
        return "Ubicación sugerida: B4-X2"
    except Exception as e:
        return f"ERROR: {str(e)}"

if __name__ == "__main__":
    svc = Service("location_optimizer", "localhost", 9002)
    svc.run_service(suggest_location)