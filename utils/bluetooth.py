import bluetooth
import asyncio
import time
import dbus
from enum import Enum

class BluetoothCommands(Enum):
    CHANGE_WALLPAPER_FULL_1 = 1
    CHANGE_WALLPAPER_FULL_2 = 2
    CHANGE_WALLPAPER_FULL_3 = 3
    CHANGE_WALLPAPER_HALF_1 = 4
    CHANGE_WALLPAPER_HALF_2 = 5
    CHANGE_WALLPAPER_HALF_3 = 6

rfcomm_client_socket = None
a2dp_client_socket = None
avrcp_client_socket = None

server_address = "XX:XX:XX:XX:XX:XX"

def initialize_bluetooth():
    global rfcomm_client_socket
    global a2dp_client_socket
    global avrcp_client_socket
    
    # 1. Set up a Bluetooth server socket (RFCOMM)
    rfcomm_server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    rfcomm_server_socket.bind(("", 1))
    rfcomm_server_socket.listen(1)

    print("Waiting for a Bluetooth RFCOMM connection...")
    rfcomm_client_socket, rfcomm_client_info = rfcomm_server_socket.accept()
    print(f"Accepted connection from {rfcomm_client_info}")

    # Set recv() so that it wont block
    rfcomm_client_socket.setblocking(0)


    # 2. Set up a Bluetooth server socket (A2DP)
    a2dp_server_socket = bluetooth.BluetoothSocket(bluetooth.A2DP)
    a2dp_server_socket.bind(("", bluetooth.A2DP_PSM))
    a2dp_server_socket.listen(2)

    print(f"Waiting for Bluetooth A2DP connection...")
    a2dp_client_socket , ad2p_client_info = a2dp_server_socket.accept()
    print(f"Accepted connection from {ad2p_client_info}")


    # 3. Set up a Bluetooth server socket (AVRCP)
    avrcp_server_socket = bluetooth.BluetoothSocket(bluetooth.AVRCP_TARGET)
    avrcp_server_socket.bind(("", bluetooth.AVRCP_PSM))
    avrcp_server_socket.listen(3)

    print(f"Waiting for Bluetooth AVRCP connection...")
    avrcp_client_socket , avrcp_client_info = avrcp_server_socket.accept()
    print(f"Accepted connection from {avrcp_client_info}")

def receive_data(): 
    # Try to get a chunk of data
    chunk = rfcomm_client_socket.recv(1)

    # If data is available
    if not chunk:
        return None
    else:
        # Get command
        command = b''
        while chunk != b'\n':
            command += chunk
            chunk = rfcomm_client_socket.recv(1)

        # Decode command (bytes -> string)
        command = bytes.decode(command, encoding="utf-8")

        # Get data
        chunk = rfcomm_client_socket.recv(1024)

        data = b''
        # While data is available
        while not chunk:
            data += chunk
            chunk = rfcomm_client_socket.recv(1024)

        # Now command and data is completely received and ready to return
        # Only command is decoded, data is completely clean and remain unprocessed
        return command, data

def on_properties_changed(interface, changed, invalidated):
    if "Connected" in changed:
        if changed["Connected"]:
            print("Bluetooth is connected.")
        else:
            print("Bluetooth is disconnected.")

async def monitor_bluetooth_connection():
    system_bus = dbus.SystemBus()

    # Replace this Bluetooth adapter's path
    adapter_path = "/org/bluez/hci0"
    adapter = system_bus.get_object("org.bluez", adapter_path)

    # Connect to the Adapter's PropertiesChanged signal
    adapter.connect_to_signal("PropertiesChanged", on_properties_changed)

    print("Monitoring Bluetooth connection status...")

    while True:
        await asyncio.sleep(1)