from common.services_mapping import services_mapping

def soa_formatter(service_name: str, data: str) -> bytes | None:
    try:
        if service_name != "sinit":
            service = services_mapping[service_name]
        else:
            service = "sinit"
    except KeyError:
        print(f"ERROR: '{service_name}' does not exist.")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None
    
    payload_length = len(service) + len(data)
    padding_length = 5 - len(str(payload_length))
    padding = ""

    for _ in range(padding_length):
        padding += "0"
    
    formatted_response = padding + str(payload_length) + service + data

    return formatted_response.encode()
