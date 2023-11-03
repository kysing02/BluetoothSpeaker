# Raspberry Pi Logic
# Team 01
from gpiozero import Button
from Status import Status, StatusEnum
import threading
from utils import bluetooth as bt
from utils import display
# PIN Setups (For Simulating Gesture Sensor Purpose)
btn1 = 5
btn2 = 6
btn3 = 13
btn4 = 19

clock_thread = None
cmd_thread = None

# Main process
def main():
    
    # Setup gesture as button (For Simulation only)
    gesture_up = Button(btn1)
    gesture_down = Button(btn2)
    gesture_left = Button(btn3)
    gesture_right = Button(btn4)

    # Initial Status
    Status.set_status(StatusEnum.WALLPAPER_FULL)

    # Initial Utils
    bt.initialize_bluetooth()
    display.initialize_display()
    

    # Set
    while True:
        # Part 1 - Check Bluetooth Incoming Data
        command, data = bt.receive_data()
        # If there is input from bluetooth
        if (command != None):
            decode_bluetooth_command(command, data)
        
        # Part 2 - Check for sensor or button
            # Change mode
    # End

def decode_bluetooth_command(command, data):
    if command == bt.BluetoothCommands.CHANGE_WALLPAPER_1:
        None