'''
Arduino Commands
0 : None
1 : Reserved
2 : AVRCP - Pause
3 : AVRCP - Play
4 : AVRCP - Stop
5 : AVRCP - Update song title
6 : AVRCP - Update song artist
7 : AVRCP - Update song cover
8 : Bluetooth - Connected
9 : Bluetooth - Disconnected
A : Change status CLOCK
B : Change status WALLPAPER_CLOCK
C : Change status MUSIC
'''
import serial
import time
from Status import Status, StatusEnum

def initialize_connection():
    global ser
    ser = serial.Serial('/dev/ttyACM0', 38400)

def send_command(ser, command, data=None):
    if data is not None:
        command += data
    ser.write(command.encode())
    time.sleep(0.1)
    
def change_status(status):
    if (status == StatusEnum.CLOCK):
        Status.set_status(StatusEnum.CLOCK)
        send_command(ser, "A")
    elif (status == StatusEnum.WALLPAPER_CLOCK):
        Status.set_status(StatusEnum.WALLPAPER_CLOCK)
        send_command(ser, "B")
    elif (status == StatusEnum.MUSIC):
        Status.set_persistent_status()
        Status.set_status(StatusEnum.MUSIC)
        send_command(ser, "C")

def avrcp_commands(command, data=None):
    '''
    Update AVRCP playback status.
    command: "pause", "play", "stop", "title", "artist", "cover"
    '''
    commandint = 0
    if command == "pause":
        commandint = 2
    elif command == "play":
        commandint = 3
    elif command == "stop":
        commandint = 4
    elif command == "title":
        commandint = 5
    elif command == "artist":
        commandint = 6
    elif command == "cover":
        commandint = 7
    send_command(ser, commandint, data)