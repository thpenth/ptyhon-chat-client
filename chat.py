import socket
import threading
import json
import sys

def listen_for_messages(port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.bind(('', port))
        print(f"Listening for messages on UDP port {port}")
        
        while True:
            message, _ = udp_socket.recvfrom(1024)

            decoded_message = message.decode('utf-8')

            message_dict = json.loads(decoded_message)
 
            user = message_dict.get('user', 'Unknown')
            text = message_dict.get('text', '')

            print(f"{user}: {text}")


def register_with_directory(directory_service_addr, user, udp_port):
    message = json.dumps({'operation': 'register', 'user': user, 'addr': f"127.0.0.1:{udp_port}"})
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.connect(directory_service_addr)
        tcp_socket.sendall(message.encode('utf-8'))

def lookup_user(directory_service_addr, user):
    message = json.dumps({'operation': 'lookup', 'user': user})
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.connect(directory_service_addr)
        tcp_socket.sendall(message.encode('utf-8'))
        response = tcp_socket.recv(1024).decode('utf-8')
    return json.loads(response)['addr']

def send_message(target, message):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.sendto(message.encode('utf-8'), target)

def main(listen_port, user, target, directory_service=None):
    threading.Thread(target=listen_for_messages, args=(listen_port,), daemon=True).start()
    
    if directory_service:
        directory_service_addr = (directory_service.split(':')[0], int(directory_service.split(':')[1]))
        register_with_directory(directory_service_addr, user, listen_port)
        if not target.count(':') == 1:  # If target is a username, not IP:port
            target_addr = lookup_user(directory_service_addr, target)
            if target_addr == 'UNKNOWN':
                print("Could not lookup user.")
                return
            target = target_addr
    
    target_ip, target_port = target.split(':')
    while True:
        message = input()
        send_message((target_ip, int(target_port)), json.dumps({'user': user, 'text': message}))

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: chat.py <listen_port> <user> <target> [<directory_service>]")
        exit(1)
    
    listen_port = int(sys.argv[1])
    user = sys.argv[2]
    target = sys.argv[3]
    directory_service = sys.argv[4] if len(sys.argv) == 5 else None
    
    main(listen_port, user, target, directory_service)
