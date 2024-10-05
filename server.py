import threading
import socket

# socket setup
PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = {} #create a dictionary instead of set
clients_lock = threading.Lock()

# Newly added function to for server to broadcast all clients
def broadcast(message, sender_addr=None):
    if sender_addr:
        formatted_message = f"[{sender_addr}]: {message}"
    else:
        formatted_message = f"[SERVER]: {message}"

    with clients_lock:
        for client in clients.values():
            client.sendall(formatted_message.encode(FORMAT))

# function for sending message to a particular client
def send_to_client(addr, message):
    with clients_lock:
        if addr in clients:
            clients[addr].sendall(f"[SERVER]: {message}".encode(FORMAT))
        else:
            print(f"[ERROR]: No client with address {addr} connected.")


def handle_client(conn, addr):
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
            broadcast(msg, sender_addr=addr)

    except ConnectionResetError:
        print(f"[ERROR] Connection with {addr} lost.")
    
    finally:
        with clients_lock:
            if addr in clients:  # Check if the address exists in clients
                del clients[addr]  # Only delete if it exists
        conn.close()
        print(f"[DISCONNECTED] {addr} disconnected.")


# function that allow server to send message to client
def start_server_broadcast():
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
    print("[SERVER STARTED]")
    server.listen()
    threading.Thread(target=start_server_broadcast).start() #use to run the start_server_broadcast function in a separate thread

    while True:
        conn, addr = server.accept()
        print(f"[NEW CONNECTION] {addr} connected.\n")
        with clients_lock:
            clients[str(addr)] = conn
            print(f"[CLIENT ADDED] Current clients: {list(clients.keys())}")  # Log current clients
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start()
