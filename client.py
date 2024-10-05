import socket
import threading
import sys
from datetime import datetime

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

# Establish a connection to the server.
def connect():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    return client

# Send a message to the server.
def send(client, msg):
    try:
        client.send(msg.encode(FORMAT))
    except Exception as e:
        print(f"[ERROR] Could not send message: {e}")

# Receive and print messages from the server.
def receive_messages(connection):
    while True:
        try:
            msg = connection.recv(1024).decode(FORMAT)
            if msg:
                sys.stdout.write("\r" + " " * len("Message (q for quit): ") + "\r")  # Clear current input
                print(msg)
                print("\nMessage (q for quit): ", end='', flush=True)  # Reprint the prompt
        except Exception as e:
            print(f"[ERROR] {e}")
            break

# def format_message(raw_message):
#     """Custom formatting for messages."""
#     current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     return f"[{current_time}] {raw_message}"

# Start the client and handle user input.
def start():
    # Ask the user if they want to connect
    answer = input("\nWould you like to connect to the server (yes/no)? ")
    if answer.lower() != 'yes':
        print("Connection aborted.")
        return

    connection = connect()

    # Prompt for username and send it to the server
    username = input("\nEnter your username: ")
    send(connection, username)

    # Start a thread to receive messages
    threading.Thread(target=receive_messages, args=(connection,)).start()

    while True:
        msg = input("Message (q for quit): ")
        if msg.lower() == 'q':
            send(connection, DISCONNECT_MESSAGE)
            break
        send(connection, msg)

    connection.close()
    print("Disconnected from server.")

if __name__ == "__main__":
    start()
