# import threading
# import socket

# PORT = 5050
# SERVER = "localhost"
# ADDR = (SERVER, PORT)
# FORMAT = "utf-8"
# DISCONNECT_MESSAGE = "!DISCONNECT"

# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.bind(ADDR)

# clients = set()
# clients_lock = threading.Lock()


# def handle_client(conn, addr):
#     print(f"[NEW CONNECTION] {addr} Connected")

#     try:
#         connected = True
#         while connected:
#             msg = conn.recv(1024).decode(FORMAT)
#             if not msg:
#                 break

#             if msg == DISCONNECT_MESSAGE:
#                 connected = False

#             print(f"[{addr}] {msg}")
#             with clients_lock:
#                 for c in clients:
#                     c.sendall(f"[{addr}] {msg}".encode(FORMAT))

#     finally:
#         with clients_lock:
#             clients.remove(conn)

#         conn.close()


# def start():
#     print('[SERVER STARTED]!')
#     server.listen()
#     while True:
#         conn, addr = server.accept()
#         with clients_lock:
#             clients.add(conn)
#         thread = threading.Thread(target=handle_client, args=(conn, addr))
#         thread.start()


# start()


# server.py
import threading
import socket

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = {}
clients_lock = threading.Lock()

def broadcast(message):
    """Broadcast a message to all clients."""
    with clients_lock:
        for client in clients.values():
            client.sendall(f"[SERVER]: {message}".encode(FORMAT))

def send_to_client(addr, message):
    """Send a message to a specific client by its address."""
    with clients_lock:
        if addr in clients:
            clients[addr].sendall(f"[SERVER]: {message}".encode(FORMAT))
        else:
            print(f"[ERROR]: No client with address {addr} connected.")

def handle_client(conn, addr):
    """Handle communication with a connected client."""
    print(f"[NEW CONNECTION] {addr} connected.")

    try:
        connected = True
        while connected:
            msg = conn.recv(1024).decode(FORMAT)
            if not msg:
                break

            if msg == DISCONNECT_MESSAGE:
                connected = False

            print(f"[{addr}] {msg}")
            broadcast(f"[{addr}] {msg}")

    except ConnectionResetError:
        print(f"[ERROR] Connection with {addr} lost.")
    
    finally:
        with clients_lock:
            del clients[addr]
        conn.close()
        print(f"[DISCONNECTED] {addr} disconnected.")

def start_server_broadcast():
    """Allow the server to send messages to all or specific clients."""
    while True:
        message = input("[SERVER MESSAGE] Enter message or 'q' to quit: ")
        if message.lower() == 'q':
            print("Server shutting down message broadcast.")
            break

        recipient = input("[SERVER MESSAGE] Send to (all/client address): ")
        if recipient.lower() == "all":
            broadcast(message)
        else:
            send_to_client(recipient, message)

def start():
    """Start the server and handle clients in separate threads."""
    print("[SERVER STARTED]")
    server.listen()
    threading.Thread(target=start_server_broadcast).start()

    while True:
        conn, addr = server.accept()
        with clients_lock:
            clients[str(addr)] = conn
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start()


