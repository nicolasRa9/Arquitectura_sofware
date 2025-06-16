import socket, threading
from common.services_mapping import services_mapping
HOST, PORT = "0.0.0.0", 5001
reg={}
def loop(sock):
    while True:
        hdr = sock.recv(10)
        if not hdr: break
        ln, code = int(hdr[:5]), hdr[5:10].decode()
        payload = sock.recv(ln-5)
        if payload.startswith(b'sinit'):
            reg[code]=sock
            print("✔ registered", code)
            continue
        dst = reg.get(code)
        if dst:
            dst.sendall(hdr+payload)
with socket.socket() as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT)); s.listen()
    print("ESB listening on 5001")
    while True:
        c,_ = s.accept()
        threading.Thread(target=loop, args=(c,), daemon=True).start()