import threading
import socket
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Server setup
PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
SMTP_SERVER = "smtp.gmail.com"  
SMTP_PORT = 587
EMAIL_ADDRESS = "rosy123@gmail.com"  # Replace with your email address
EMAIL_PASSWORD = "xxxxxxx"  # Replace with your email password

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = {}
usernames = set()
emails = {}  # Store the email addresses associated with clients
clients_lock = threading.Lock()
message_log = []

# Function to send email notifications via SMTP
def send_email_notification(to_email, subject, message_body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message_body, 'plain'))

    try:
        smtp_server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        smtp_server.starttls()
        smtp_server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp_server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        smtp_server.quit()
        print(f"\n[EMAIL SENT] Notification sent to {to_email}.")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")

# Broadcast a message to all clients except the sender
def broadcast(message, sender_name=None, exclude_client=None):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if sender_name:
        formatted_message = f"\n[{timestamp}] {sender_name}: {message}"
    else:
        formatted_message = f"\n[{timestamp}] {message}"

    with clients_lock:
        for client, client_conn in clients.items():
            if client_conn != exclude_client:  # Skip sending back to sender
                try:
                    client_conn.sendall(formatted_message.encode(FORMAT))
                except Exception as e:
                    print(f"[ERROR] Failed to send message to client: {e}")

# Handle communication with a connected client
def handle_client(conn, addr):
    print(f"\n[NEW CONNECTION] {addr} connected.")
    
    try:
        # recieve the username and email from client side
        username = conn.recv(1024).decode(FORMAT)

        user_email = conn.recv(1024).decode(FORMAT)

        if username in usernames:
            conn.sendall("\nUsername already taken. Disconnecting.".encode(FORMAT))
            conn.close()
            return

        with clients_lock:
            clients[addr] = conn
            usernames.add(username)
            emails[addr] = user_email

        # Notify the client they have joined
        conn.sendall(f"\nWelcome, {username}! You have joined the chat.".encode(FORMAT))

        # Notify all other clients that a new user has joined
        broadcast(f"\n{username} has joined the chat!", exclude_client=conn)

        connected = True
        while connected:
            msg = conn.recv(1024).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
                broadcast(f"{username} has left the chat.", exclude_client=conn)
                break
            elif msg:
                # Log the message
                message_log.append(f"{username}: {msg}")

                # Broadcast the message to other clients
                broadcast(msg, sender_name=username)

                # Send email notifications to all clients except the sender
                with clients_lock:
                    for client_addr, client_conn in clients.items():
                        if client_conn != conn:  # Skip the sender
                            client_email = emails[client_addr]
                            email_subject = f"New message from {username}"
                            email_body = f"You received a new message from user {username}:\n Sender email: {user_email}\n\n{msg}"
                            # Send the email in a separate thread
                            threading.Thread(target=send_email_notification, args=(client_email, email_subject, email_body)).start()

    except Exception as e:
        print(f"[ERROR] {addr} encountered an issue: {e}")
    
    finally:
        with clients_lock:
            if addr in clients:
                del clients[addr]
                usernames.remove(username)
                del emails[addr]
        conn.close()
        print(f"\n[DISCONNECTED] {addr} disconnected.")

# Start the server and handle incoming connections
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

