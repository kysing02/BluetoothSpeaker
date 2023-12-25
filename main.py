# Raspberry Pi Logic (Mainly AVRCP control)
# Team 01
from gpiozero import Button
from Status import Status, StatusEnum
import arduino_control

import dbus, dbus.mainloop.glib, sys
from gi.repository import GLib
import requests
from PIL import Image

import threading

LASTFM_API_KEY = '69d8496cb54a33f47e7a38991f1eba9e'

# PIN Setups (For Simulating Gesture Sensor Purpose)
UP = 17
DOWN = 27
LEFT = 22
RIGHT = 5
CLOCKWISE = 6
ANTICLOCKWISE = 26
WAVE = 23

# Music playback status
playback_status = "stopped"

# Main process
def main():
    # Setup gesture as button (For Simulation only)
    up = Button(UP)
    down = Button(DOWN)
    left = Button(LEFT)
    right = Button(RIGHT)
    clockwise = Button(CLOCKWISE)
    anticlockwise = Button(ANTICLOCKWISE)
    wave = Button(WAVE)
    
    # Initial Status
    arduino_control.change_status(StatusEnum.CLOCK)

    # Set sensor or button events
    up.when_activated = lambda : change_status("up")
    down.when_activated = lambda : change_status("down")
    left.when_activated = lambda : change_status("left")
    right.when_activated = lambda : change_status("right")
    clockwise.when_activated = lambda : change_status("clockwise")
    anticlockwise.when_activated = lambda : change_status("anticlockwise")
    wave.when_activated = lambda : change_status("wave")

    # AVRCP Setup
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    obj = bus.get_object('org.bluez', "/")
    mgr = dbus.Interface(obj, 'org.freedesktop.DBus.ObjectManager')
    global player_iface, transport_prop_iface
    player_iface = None
    transport_prop_iface = None
    for path, ifaces in mgr.GetManagedObjects().items():
        if 'org.bluez.MediaPlayer1' in ifaces:
            player_iface = dbus.Interface(
                    bus.get_object('org.bluez', path),
                    'org.bluez.MediaPlayer1')
        elif 'org.bluez.MediaTransport1' in ifaces:
            transport_prop_iface = dbus.Interface(
                    bus.get_object('org.bluez', path),
                    'org.freedesktop.DBus.Properties')
    if not player_iface:
        sys.exit('Error: Media Player not found.')
    if not transport_prop_iface:
        sys.exit('Error: DBus.Properties iface not found.')

    bus.add_signal_receiver(
            on_property_changed,
            bus_name='org.bluez',
            signal_name='PropertiesChanged',
            dbus_interface='org.freedesktop.DBus.Properties')

    # Create a thread for reading input
    input_thread = threading.Thread(target=debug_read_input)

    # Set the thread as a daemon so it will exit when the main program exits
    input_thread.daemon = True

    # Start the input thread
    input_thread.start()

    # Run the main loop
    GLib.MainLoop().run()

def debug_read_input():
    while True:
        signal_input = input("Enter gesture input: ")
        change_status(signal_input)
    
def change_status(action):
    '''
    Change status when an input is detected.
    action list.
    action: "up" "down" "left" "right" "clockwise" "anticlockwise" "wave"
    '''
    # DEBUG
    print("Button pressed: " + str(action))
    
    # Check current status
    current_status = Status.get_status()
    
    if current_status == StatusEnum.CLOCK:
        if action == "left":
            arduino_control.change_status(StatusEnum.WALLPAPER_CLOCK)
        elif action == "up":
            arduino_control.change_status(StatusEnum.MUSIC)
            
    elif current_status == StatusEnum.WALLPAPER_CLOCK:
        if action == "right":
            arduino_control.change_status(StatusEnum.CLOCK)
        elif action == "up":
            arduino_control.change_status(StatusEnum.MUSIC)

    elif current_status == StatusEnum.CLOCK:
        if action == "down":
            arduino_control.change_status(StatusEnum.get_persistent_status())
        elif action == "right":
            arduino_control.avrcp_commands()

    if True: #any
        if action == "wave":
            playback_control("pp")
        elif action == "clockwise":
            playback_control("vol-up")
        elif action == "anticlockwise":
            playback_control("vol-down")

# AVRCP Control
def on_property_changed(interface, changed, invalidated):
    global playback_status
    if interface != 'org.bluez.MediaPlayer1':
        return
    for prop, value in changed.items():
        if prop == 'Status':
            print('Playback Status: {}'.format(value))
            if (value == "playing"):
                playback_status = value
                arduino_control.avrcp_commands("play")
            elif (value == "paused"):
                playback_status = value
                arduino_control.avrcp_commands("pause")
            elif (value == "stopped"):
                playback_status = value
                arduino_control.avrcp_commands("stop")
        elif prop == 'Track':
            print('Music Info:')
            for key in ('Title', 'Artist'):
                print('   {}: {}'.format(key, value.get(key, '')))
            cover_art = get_and_process_album_art(value.get('Artist', ''), value.get('Album', ''))
            arduino_control.avrcp_commands("title", value.get('Title', ''))
            arduino_control.avrcp_commands("artist", value.get('Artist', ''))
            arduino_control.avrcp_commands("cover", str(cover_art))
            print(str(cover_art))                   # Debug

def playback_control(command):
    '''
    Provide playback control for AVRCP
    command: "play", "pause", "next", "prev", "vol-up", "vol-down", "pp"(playpause)
    '''
    str = command
    if str.startswith('play'):
        player_iface.Play()
    elif str.startswith('pause'):
        player_iface.Pause()
    elif str.startswith('pp'):
        if playback_status == "playing":
            player_iface.Pause()
        if playback_status == "paused":
            player_iface.Play()
    elif str.startswith('next'):
        player_iface.Next()
    elif str.startswith('prev'):
        player_iface.Previous()
    elif str.startswith('vol'):
        currentVol = transport_prop_iface.Get(
                'org.bluez.MediaTransport1',
                'Volume')
        addVol = 0
        if (str == 'vol-up'):
            addVol = 10
        elif (str == 'vol-down'):
            addVol = -10
        newVol = clamp(currentVol + addVol, 0 , 127)
        transport_prop_iface.Set(
                'org.bluez.MediaTransport1',
                'Volume',
                dbus.UInt16(newVol))
    return True

def get_and_process_album_art(artist, album):
    if not artist or not album:
        print('Cannot fetch album art without artist and album information.')
        return None

    try:
        response = requests.get(f'http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key={LASTFM_API_KEY}&artist={artist}&album={album}&format=json')
        data = response.json()
        image_url = data.get('album', {}).get('image', [])[-1].get('#text', '')
        print('Album Art URL:', image_url)

        processed_image = process_image(image_url)

        pixel_values = list(processed_image.getdata())
        pixel_data = [int(value) for pixel in pixel_values for value in pixel if pixel.index(value) % 4 != 3]
        compressed_data = convert_to_16_bit(pixel_data);
        # Return the processed data ready to send
        return compressed_data
    
    except Exception as e:
        print('Error fetching or processing album art:', str(e))
        return None

def convert_to_16_bit(input_data):
    # Check if the input has a valid length
    if len(input_data) % 3 != 0:
        raise ValueError("Input data length must be a multiple of 3 (representing RGB values).")

    # Convert 8-bit RGB values to 16-bit RGB values
    output_data = []
    for i in range(0, len(input_data), 3):
        r = input_data[i]
        g = input_data[i + 1]
        b = input_data[i + 2]

        # Combine the three 8-bit values into a single 16-bit value (5 bits for red, 6 bits for green, 5 bits for blue)
        rgb_16_bit = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        
        output_data.append(rgb_16_bit)

    return output_data

def process_image(image_url):
    if not image_url:
        print('Image URL not available.')
        return None

    response = requests.get(image_url)
    if response.status_code == 200:
        with open('album_art.jpg', 'wb') as f:
            f.write(response.content)

        # Open the downloaded image
        original_image = Image.open('album_art.jpg')

        # Resize the image to 64x32
        resized_image = original_image.resize((64, 32))

        # Convert the image to a bitmap (if needed)
        bitmap_image = resized_image.convert("1")

        return bitmap_image
    else:
        print('Failed to download image. Status Code:', response.status_code)
        return None

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

if __name__ == "__main__":
    main() 

'''
TODO
1. To monitor bluetooth connection and establish auto reconnect feature, maybe use "Error" status from MediaPlayer1?
'''