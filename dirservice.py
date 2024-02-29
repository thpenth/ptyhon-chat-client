import socket
import threading
import json

def client_handler(connection):
    while True:
        try:
            data = connection.recv(1024)
            if not data:
                break
            
            request = json.loads(data.decode('utf-8'))
            operation = request['operation']
            
            if operation == 'register':
                directory[request['user']] = request['addr']
                print(f"Registered {request['user']} at {request['addr']}")
            elif operation == 'lookup':
                addr = directory.get(request['user'], 'UNKNOWN')
                connection.sendall(json.dumps({'addr': addr}).encode('utf-8'))
        except Exception as e:
            print(f"Error: {e}")
            break

def start_directory_service(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('', port))
        server_socket.listen()
        print(f"Directory Service is listening on port {port}.")

        while True:
            conn, _ = server_socket.accept()
            threading.Thread(target=client_handler, args=(conn,), daemon=True).start()

if __name__ == '__main__':
    import sys
    PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 12345
    directory = {}
    start_directory_service(PORT)
