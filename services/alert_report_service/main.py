import os, socket, threading, time, random, string

BUS_HOST = os.getenv("BUS_HOST", "bus_service")
BUS_PORT = int(os.getenv("BUS_PORT", "9000"))
SERVICE_NAME = os.getenv("SERVICE_NAME", "alertrep")
MSG_SIZE = 10

def recv_loop(sock):
    while True:
        data = sock.recv(MSG_SIZE)
        if not data:
            break
        print(f"[{SERVICE_NAME}] <- {data}")

def send_loop(sock):
    while True:
        # Example payload: first char identifies service, rest random
        payload_raw = (SERVICE_NAME[:1] + ''.join(random.choices(string.ascii_uppercase, k=MSG_SIZE-1)))[:MSG_SIZE]
        payload = payload_raw.encode()
        sock.sendall(payload)
        print(f"[{SERVICE_NAME}] -> {payload}")
        time.sleep(5)

def main():
    time.sleep(2)  # wait for bus readiness
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((BUS_HOST, BUS_PORT))
    threading.Thread(target=recv_loop, args=(sock,), daemon=True).start()
    send_loop(sock)

if __name__ == "__main__":
    main()
