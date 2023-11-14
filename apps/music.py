import dbus
# FOR DEBUG ONLY
from PIL import Image
import io

# The code below here is for AVRCP
def on_playback_changed(interface, changed, invalidated, path, props):
    if "PlaybackStatus" in changed:
        status = props.Get(interface, "PlaybackStatus")
        print(f"Playback Status: {status}")

def play_pause_media():
    session_bus = dbus.SessionBus()
    macos_device = "org.bluez.MediaControl1"
    # Replace with macOS device MAC Address
    player = "/org/bluez/hci0/dev_3C_22_FB_9D_ED_76/player0"

    obj = session_bus.get_object(macos_device, player)
    interface = dbus.Interface(obj, "org.bluez.MediaControl1")

    interface.PlayPause()
    print("Play Pause")

# TODO Show media Image after saving cover art
def show_media_image():
    session_bus = dbus.SessionBus()
    macos_device = "org.bluez.MediaControl1"
    # Replace with macOS device MAC Address
    player = "/org/bluez/hci0/dev_3C_22_FB_9D_ED_76/player0"

    obj = session_bus.get_object(macos_device, player)
    interface = dbus.Interface(obj, "org.bluez.MediaControl1")

    metadata = interface.GetProperties()
    if "Track" in metadata:
        track_info = metadata["Track"]
        if "CoverArt" in track_info:
            cover_art = track_info["CoverArt"]
            print(f"Cover Art: {cover_art}")
            image = Image.open(io.BytesIO(cover_art))
            image.save("test/test_cover_art.png")

# def send_mpris_command(command):
#     session_bus = dbus.SessionBus()
#     macos_device = "org.mpris.MediaPlayer2"
#     # Replace with macOS device MAC Address
#     player = "/org/bluez/hci0/dev_XX_XX_XX_XX_XX_XX/player0"

#     obj = session_bus.get_object(macos_device, player)
#     interface = dbus.Interface(obj, "org.bluez.MediaControl1")

def glib_mainloop_task():
    loop = GLib.MainLoop()
    loop.run()