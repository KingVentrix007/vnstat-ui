import socket
import json

SOCKET_PATH = "/tmp/nethogs_service.sock"

with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
    s.connect(SOCKET_PATH)
    s.sendall(b"get")
    data = b""
    print("Waiting")
    while True:
        chunk = s.recv(65536)
        print(chunk)

        if not chunk:
            break
        data += chunk
        print(data)

totals = json.loads(data.decode())
print(totals)
