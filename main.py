# Raspberry Pi Logic
# Team 01
from gpiozero import Button
from Status import Status, StatusEnum
import threading

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

    # Set
    # If there is input from bluetooth
        # Decode Bluetooth command
    # Else if there is sensor or button value
        # Change mode
    # End