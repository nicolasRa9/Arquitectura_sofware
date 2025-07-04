import socket

SERVICE_CODE = b'MOVE1'

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bus_address = ('localhost', 5000)
    print('connecting to {} port {}'.format(*bus_address))
    sock.connect(bus_address)

    try:
        message = b'00010sinit' + SERVICE_CODE
        print('sending {!r}'.format(message))
        sock.sendall(message)
        sinit = 1

        while True:
            print("Waiting for transaction")
            amount_received = 0
            amount_expected = int(sock.recv(5))

            while amount_received < amount_expected:
                data = sock.recv(amount_expected - amount_received)
                amount_received += len(data)
            print("Procesing ...")
            print('received {!r}'.format(data))
            if sinit == 1:
                sinit = 0
                print('Received sinit answer')
            else:
                print("Send answer")
                message = b'00013' + SERVICE_CODE + b'OK'
                print('sending {!r}'.format(message))
                sock.sendall(message)
    finally:
        print('closing socket')
        sock.close()

if __name__ == "__main__":
    main()