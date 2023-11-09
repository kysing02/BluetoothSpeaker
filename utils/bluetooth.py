import bluetooth
from enum import Enum

class BluetoothCommands(Enum):
    CHANGE_WALLPAPER_FULL_1 = 1
    CHANGE_WALLPAPER_FULL_2 = 2
    CHANGE_WALLPAPER_FULL_3 = 3
    CHANGE_WALLPAPER_HALF_1 = 4
    CHANGE_WALLPAPER_HALF_2 = 5
    CHANGE_WALLPAPER_HALF_3 = 6

client_socket = None
def initialize_bluetooth():
    global client_socket
    
    # Set up a Bluetooth server socket
    server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_socket.bind(("", 1))
    server_socket.listen(1)

    print("Waiting for a Bluetooth connection...")

    client_socket, client_info = server_socket.accept()
    print(f"Accepted connection from {client_info}")

    # Set recv() so that it wont block
    client_socket.setblocking(0)

def receive_data(): 
    # Try to get a chunk of data
    chunk = client_socket.recv(1)

    # If data is available
    if not chunk:
        return None
    else:
        # Get command
        command = b''
        while chunk != b'\n':
            command += chunk
            chunk = client_socket.recv(1)

        # Decode command (bytes -> string)
        command = bytes.decode(command, encoding="utf-8")

        # Get data
        chunk = client_socket.recv(1024)

        data = b''
        # While data is available
        while not chunk:
            data += chunk
            chunk = client_socket.recv(1024)

        # Now command and data is completely received and ready to return
        # Only command is decoded, data is completely clean and remain unprocessed
        return command, data
    
# TODO: Bluetooth通信が来たら(もしくは通信が切断されたら)、main.pyのnofify_connection_change("disconnect")関数に知らせる