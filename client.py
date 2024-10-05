import socket
import time
import threading

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"


def connect():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    return client


def send(client, msg):
    message = msg.encode(FORMAT)
    client.send(message)

# newly added function to recieve the message from server or other client
def receive_messages(connection):
    while True:
        try:
            msg = connection.recv(1024).decode(FORMAT)
            if msg:
                print(f"{msg}\n", end="")  # Use end="" to avoid an extra newline
                print("Message (q for quit): ", end='', flush=True)
        except Exception as e:
            print(f"[ERROR] {e}")
            break

def start():
    answer = input('Would you like to connect (yes/no)? ')
    if answer.lower() != 'yes':
        return

    connection = connect()
    threading.Thread(target=receive_messages, args=(connection,)).start()  # Start receiving messages

    while True:
        msg = input("Message (q for quit): ")
        if msg == 'q':
            break

        send(connection, msg)

    send(connection, DISCONNECT_MESSAGE)
    time.sleep(1)
    print('Disconnected')


start()
