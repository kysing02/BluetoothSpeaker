"""
This is the program to communicate with ESP32.

ESP32と通信を行うためのプログラム。

ESP32 Commands（ESP32命令）
0 : None（なし）
1 : Bluetooth - Connected（接続）/ Disconnected（切断）
2 : AVRCP - Pause（停止）
3 : AVRCP - Play（再生）
4 : AVRCP - Stop（終了）
5 : AVRCP - Update song title（曲のタイトルを更新する）
6 : AVRCP - Update song artist（曲の作家名を更新する）
7 : AVRCP - Update song cover（曲の画像を更新する）
8 : System - Set datetime　（日付を設定する）("%x:%H:%M:%S")
9 : 
A : Change status CLOCK（ステータス更新 - 時計モード）
B : Change status WALLPAPER_CLOCK（ステータス更新 - 時計壁紙モード）
C : Change status MUSIC（ステータス更新 - 音楽モード）
D : Change status WEATHER (ステータス更新 - 天気予報モード)
"""

import serial
import time
from Status import Status, StatusEnum
    
def initialize_connection(port='/dev/ttyUSB0', baud_rate=38400): 
    """Initialize serial connection with ESP32.

    ESP32間シリアル通信を初期化する。

    Args:
        port (str, optional): Port to connect. Defaults to '/dev/ttyACM0'.
        baud_rate (int, optional): Baud rate of ESP32. Defaults to 38400.
    """
    global ser
    ser = serial.Serial(port, baud_rate)

def send_command(command, data=None):
    """Send command to serial port. Data is optional.

    シリアルポートにコマンドを送信する。データは任意。

    Args:
        command (char): Command in type of single character.
        data (str, optional): Data information to send. Defaults to None.
    """
    if data is not None:
        command = command + data + '\n'
    else:
        command = command
    ser.write(command.encode())
    print("Sent: ", command)
    time.sleep(0.1)
    
def change_status(status):
    """Notify ESP32 about change in current status.

    ESP32にステータスの更新を知らせる。
    
    Args:
        status (StatusEnum): Change to status.
    """
    if (status == StatusEnum.CLOCK):
        Status.set_status(StatusEnum.CLOCK)
        send_command("A")
    elif (status == StatusEnum.WALLPAPER_CLOCK):
        Status.set_status(StatusEnum.WALLPAPER_CLOCK)
        send_command("B")
    elif (status == StatusEnum.MUSIC):
        Status.set_persistent_status()
        Status.set_status(StatusEnum.MUSIC)
        send_command("C")
    elif (status == StatusEnum.WEATHER):
        Status.set_status(StatusEnum.WEATHER)
        send_command("D")

def avrcp_commands(command, data=None):
    """Update AVRCP playback status.

    AVRCPの音楽に関する情報を更新する。

    Args:
        command (str): "pause", "play", "stop", "title", "artist", "cover", "bluetooth", 
                        "datetime", "weather", "temperature"
        data (str, optional): Data to send. Defaults to None.
    """
    command_int = 'X'
    if command == "bluetooth":
        command_int = '1'
    elif command == "pause":
        command_int = '2'
    elif command == "play":
        command_int = '3'
    elif command == "stop":
        command_int = '4'
    elif command == "title":
        command_int = '5'
    elif command == "artist":
        command_int = '6'
    elif command == "cover":
        command_int = '7'
    elif command == "datetime":
        command_int = '8'
    elif command == "weather":
        command_int = '9'
    elif command == "temperature":
        command_int = '0'
    send_command(command_int, data)
