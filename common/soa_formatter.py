from .services_mapping import services_mapping

def soa_formatter(service_name: str, data: str) -> bytes | None:
    """
    Empaqueta un mensaje siguiendo el protocolo SOA.
    Formato: [5 bytes length][service_code][data]
    """
    try:
        service = services_mapping[service_name] if service_name != "sinit" else "sinit"
    except KeyError:
        print(f"ERROR: '{service_name}' does not exist.")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None

    payload_length = len(service) + len(data)
    return f"{payload_length:05d}{service}{data}".encode()
