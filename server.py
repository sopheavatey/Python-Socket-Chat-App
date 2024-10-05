import threading
import socket
from datetime import datetime

# Server setup
PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = {}
usernames = set()
clients_lock = threading.Lock()
message_log = []  # To store all messages sent in the chat

# Broadcast a message to all connected clients, except the one that sent it.
def broadcast(message, sender_name=None, exclude_client=None):
 
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if sender_name:
        formatted_message = f"\n[{timestamp}] {sender_name}: {message}"
    else:
        formatted_message = f"\n[{timestamp}] {message}"

    with clients_lock:
        for client, client_conn in clients.items():
            if client_conn != exclude_client:  # Skip sending the message back to the sender
                try:
                    client_conn.sendall(formatted_message.encode(FORMAT))
                except Exception as e:
                    print(f"[ERROR] Failed to send message to client: {e}")

# Handle communication with a connected client.
def handle_client(conn, addr):
    """Handle communication with a connected client."""
    print(f"\n[NEW CONNECTION] {addr} connected.")
    
    try:
        # Receive username and ensure it's unique
        username = conn.recv(1024).decode(FORMAT)
        if username in usernames:
            conn.sendall("Username already taken. Disconnecting.".encode(FORMAT))
            conn.close()
            return

        with clients_lock:
            clients[addr] = conn
            usernames.add(username)

        # Announce to the client that they joined
        conn.sendall("You joined the server.".encode(FORMAT))
        
        # Announce to everyone else that this user has joined
        broadcast(f"{username} has joined the chat!", exclude_client=conn)

        connected = True
        while connected:
            msg = conn.recv(1024).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
                broadcast(f"\n{username} has left the chat.", exclude_client=conn)
                break
            elif msg:
                # Log the message
                message_log.append(f"{username}: {msg}")
                
                # Broadcast the message to other clients
                broadcast(msg, sender_name=username)

    except Exception as e:
        print(f"[ERROR] {addr} encountered an issue: {e}")
    
    finally:
        with clients_lock:
            if addr in clients:
                del clients[addr]
                usernames.remove(username)
        conn.close()
        print(f"\n[DISCONNECTED] {addr} disconnected.")

# Start the server and handle incoming connections.
def start():
    print("[SERVER STARTED]")
    server.listen()

    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
    except KeyboardInterrupt:
        print("\n[SERVER SHUTTING DOWN]")
    finally:
        server.close()

if __name__ == "__main__":
    start()
