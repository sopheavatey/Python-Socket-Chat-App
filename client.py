# import socket
# import time

# PORT = 5050
# SERVER = "localhost"
# ADDR = (SERVER, PORT)
# FORMAT = "utf-8"
# DISCONNECT_MESSAGE = "!DISCONNECT"


# def connect():
#     client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     client.connect(ADDR)
#     return client


# def send(client, msg):
#     message = msg.encode(FORMAT)
#     client.send(message)


# def start():
#     answer = input('Would you like to connect (yes/no)? ')
#     if answer.lower() != 'yes':
#         return

#     connection = connect()
#     while True:
#         msg = input("Message (q for quit): ")

#         if msg == 'q':
#             break

#         send(connection, msg)

#     send(connection, DISCONNECT_MESSAGE)
#     time.sleep(1)
#     print('Disconnected')


# start()

# client.py
import socket
import threading

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

def connect():
    """Establish a connection to the server."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    return client

def receive_messages(client):
    """Listen for incoming messages from the server or other clients."""
    while True:
        try:
            msg = client.recv(1024).decode(FORMAT)
            if msg:
                print(msg)
        except ConnectionResetError:
            print("Connection lost from server.")
            break

def send_messages(client):
    """Send messages to the server."""
    while True:
        msg = input("Message (q for quit): ")
        if msg == 'q':
            client.send(DISCONNECT_MESSAGE.encode(FORMAT))
            break
        client.send(msg.encode(FORMAT))

def start():
    """Start the client and initiate message sending and receiving."""
    connection = connect()

    # Create a thread to listen for messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(connection,))
    receive_thread.start()

    # In the main thread, send messages to the server
    send_messages(connection)
    receive_thread.join()

    connection.close()
    print('Disconnected')

if __name__ == "__main__":
    start()

