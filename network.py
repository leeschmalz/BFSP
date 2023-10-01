import socket
import pickle

def start_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', port))
    server_socket.listen(5)

    return server_socket

def broadcast(message, ports):
    serialized_message = pickle.dumps(message)
    for port in ports:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('127.0.0.1', port))
            client_socket.send(serialized_message)
            client_socket.close()
        except ConnectionRefusedError:
            continue
        except TimeoutError:
            print(f"Connection timed out on port {port}")
            continue