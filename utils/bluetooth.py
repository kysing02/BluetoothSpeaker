import bluetooth

# Set the Bluetooth device name and service UUID
device_name = "Bluetooth Speaker PI"
service_uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

# Set up a Bluetooth server socket
server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)