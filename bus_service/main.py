import socket, threading

HOST = '0.0.0.0'
PORT = 9000
MSG_SIZE = 10  # fixed-size bus messages (10 bytes)

clients = []

def handle_client(conn, addr):
    try:
        while True:
            data = conn.recv(MSG_SIZE)
            if not data:
                break
            # Broadcast to all other clients
            for c in clients:
                if c is not conn:
                    try:
                        c.sendall(data)
                    except Exception:
                        pass
    finally:
        conn.close()
        if conn in clients:
            clients.remove(conn)
        print(f"Client {addr} disconnected.")

def main():
    print(f"Starting bus on {HOST}:{PORT} with frame size {MSG_SIZE} bytes.")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            clients.append(conn)
            print(f"Client {addr} connected.")
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
