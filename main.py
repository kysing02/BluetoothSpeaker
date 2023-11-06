# Raspberry Pi Logic
# Team 01
import asyncio
from gpiozero import Button
from Status import Status, StatusEnum
from apps import wallpaper_clock, wallpaper, clock
from utils import bluetooth as bt
from utils import display
# PIN Setups (For Simulating Gesture Sensor Purpose)
btn1 = 5
btn2 = 6
btn3 = 13
btn4 = 19
btn5 = None
btn6 = None

app_task = None

# Main process
async def main():
    global app_task
    
    # Setup gesture as button (For Simulation only)
    g1 = Button(btn1)
    g2 = Button(btn2)
    g3 = Button(btn3)
    g4 = Button(btn4)
    g5 = Button(btn5)
    g6 = Button(btn6)
    
    # Initial Status
    Status.set_status(StatusEnum.WALLPAPER_CLOCK)
    app_task = asyncio.create_task(wallpaper_clock.display_wallpaper_clock())
    
    # Initial Utils
    bt.initialize_bluetooth()
    display.initialize_display()

    # Set sensor or button events
    g1.when_activated = lambda : change_status("g1")
    g2.when_activated = lambda : change_status("g2")
    g3.when_activated = lambda : change_status("g3")
    g4.when_activated = lambda : change_status("g4")
    g5.when_activated = lambda : change_status("g5")
    g6.when_activated = lambda : change_status("g6")
    
    # Check Bluetooth Incoming Data
    while True:
        command, data = bt.receive_data()
        # If there is input from bluetooth
        if (command != None):
            decode_bluetooth_command(command, data)
        await asyncio.sleep(0.1)

def decode_bluetooth_command(command, data):
    if command == bt.BluetoothCommands.CHANGE_WALLPAPER_FULL_1:
        wallpaper.save_wallpaper(1, "full", data)
    elif command == bt.BluetoothCommands.CHANGE_WALLPAPER_FULL_2:
        wallpaper.save_wallpaper(2, "full", data)
    elif command == bt.BluetoothCommands.CHANGE_WALLPAPER_FULL_3:
        wallpaper.save_wallpaper(3, "full", data)
    elif command == bt.BluetoothCommands.CHANGE_WALLPAPER_HALF_1:
        wallpaper.save_wallpaper(1, "half", data)
    elif command == bt.BluetoothCommands.CHANGE_WALLPAPER_HALF_2:
        wallpaper.save_wallpaper(2, "half", data)
    elif command == bt.BluetoothCommands.CHANGE_WALLPAPER_HALF_3:
        wallpaper.save_wallpaper(3, "half", data)

def change_status(action):
    '''
    Change status when an input is detected.
    action list:
    "g1" "g2" "g3" "g4" "g5" "g6"
    '''
    global app_task
    
    # Check current status
    current_status = Status.get_status()
    
    if current_status == StatusEnum.WALLPAPER_CLOCK:
        if action == "g2":
            Status.set_status(StatusEnum.CLOCK_FULL)
            app_task.cancel()
            app_task = asyncio.create_task(clock.display_clock("full"))
            
        elif action == "g3":
            Status.set_status(StatusEnum.WALLPAPER_FULL)
            app_task.cancel()
            app_task = asyncio.create_task(wallpaper.display_wallpaper(0, "full"))

        elif action == "g5":
            app_task.cancel()
            wallpaper_clock.change_wallpaper(1)
            app_task = asyncio.create_task(wallpaper_clock.display_wallpaper_clock(0))

    elif current_status == StatusEnum.WALLPAPER_FULL:
        if action == "g2":
            Status.set_status(StatusEnum.WALLPAPER_CLOCK)
            app_task.cancel()
            app_task = asyncio.create_task(wallpaper_clock.display_wallpaper_clock(0))

        elif action == "g4":
            app_task.cancel()
            wallpaper.change_wallpaper(1, "full")
            app_task = asyncio.create_task(wallpaper.display_wallpaper(0, "full"))

        elif action == "g5":
            app_task.cancel()
            wallpaper.change_wallpaper(-1, "full")
            app_task = asyncio.create_task(wallpaper.display_wallpaper(0, "full"))

    elif current_status == StatusEnum.CLOCK_FULL:
        if action == "g3":
            app_task.cancel()
            wallpaper_clock.display_wallpaper_clock(0)

asyncio.run(main())