#!/usr/bin/python
"""
Raspberry Piの制御メインプログラム。
システム設計 1班

このメインプログラムでは、主に、デバイスとのAVRCP制御、ESP32との通信、およびジェスチャーセンサの入力を処理するためのメインプログラムである。
"""
# ジェスチャーセンサの代わりにボタンを使っている
# from gpiozero import Button
from grove_gesture_sensor import gesture

# 他の自作プログラムをインポートする
from Status import Status, StatusEnum
import arduino_control

# AVRCP制御用のライブラリ
import dbus, dbus.mainloop.glib, sys
from gi.repository import GLib

# 読み取った画像を処理するためのライブラリ
# インターネットから曲の画像を検索する→読み取った画像を32x32サイズと32ビットカラー(RGBA)にする→ESP32に画像を送信する
from PIL import Image

# コマンドラインの入力を処理するために使う
import threading

# インターネットから画像を検索してリンクを探すためのライブラリ
from urllib.parse import urlparse
import requests
import bs4

# 音量操作モジュール
import alsaaudio

# ローカル時間モジュール
import time

# 音量操作
initial_volume = 30         #初期音量

# Bluetooth状況
bluetooth_available = False

# 画像検索のためのURLテンプレート
URL = 'https://www.google.com/search?tbm=isch&q='
HEADER = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}

# ジェスチャーセンサの代わりに用いるPIN設置
# UP = 17
# DOWN = 27
# LEFT = 22
# RIGHT = 5
# CLOCKWISE = 6
# ANTICLOCKWISE = 26
# WAVE = 23

# 音楽再生ステータス "None", "stopped", "playing", "paused"
playback_status = "None"

# Cache song infos（音楽情報のキャッシュ）
cacheTitle = "No Title"
cacheArtist = "No Artist"
cacheAlbum = "No Album"

# Main process
def main():
    global bluetooth_available
    bluetooth_available = False
    # ジェスチャーセンサの代わりにボタンを用いてシミュレーションをする
    # up = Button(UP)
    # down = Button(DOWN)
    # left = Button(LEFT)
    # right = Button(RIGHT)
    # clockwise = Button(CLOCKWISE)
    # anticlockwise = Button(ANTICLOCKWISE)
    # wave = Button(WAVE)
    
    # 初期化する
    arduino_control.initialize_connection()
    arduino_control.change_status(StatusEnum.CLOCK)

    # ボタンが押されたときのイベントのコールバック関数
    # up.when_activated = lambda : change_status("up")
    # down.when_activated = lambda : change_status("down")
    # left.when_activated = lambda : change_status("left")
    # right.when_activated = lambda : change_status("right")
    # clockwise.when_activated = lambda : change_status("clockwise")
    # anticlockwise.when_activated = lambda : change_status("anticlockwise")
    # wave.when_activated = lambda : change_status("wave")

    # AVRCPを初期化する
    while (bluetooth_available == False):
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
            print('Error: Media Player not found. Retrying...')
        else:
            bluetooth_available = True
        if not transport_prop_iface:
            print('Error: DBus.Properties iface not found. Retrying...')
            time.sleep(5)
        else:
            bluetooth_available = True

        objects = mgr.GetManagedObjects()
        for path, ifaces in objects.items():
            adapter = ifaces.get('org.freedesktop.DBus.Properties')
            if adapter is None:
                continue
            print(path)
            break
        track =  adapter.get('Track')
        print(track)

    # AVRCPに音楽再生情報に変更が起こったとき、ラズパイに知らせる
    bus.add_signal_receiver(
            on_property_changed,
            bus_name='org.bluez',
            signal_name='PropertiesChanged',
            dbus_interface='org.freedesktop.DBus.Properties')
    
    # 音量操作初期化
    global mixer
    mixer = alsaaudio.Mixer(control='Master')
    mixer.setvolume(initial_volume)
    
    # Note: このプログラムでは二つのスレッドが同時に実行され、一つ目は入力処理のスレッド、もう一つはAVRCP通信用のスレッド

    # 時間を読み取る
    timeinfo = time.strftime("%x:%H:%M:%S")
    print(timeinfo)
    arduino_control.avrcp_commands("datetime", timeinfo)

    # ESP32の方にBluetooth接続完了&準備完了のお知らせをする
    arduino_control.avrcp_commands("bluetooth", '1')

    # ジェスチャセンサーを初期化する
    g = gesture()
    g.init()
    g.when_activated = lambda x : change_status(x)
    
    # 入力を読み取るためのスレッドを設定する
    input_thread = threading.Thread(target=debug_read_input)

    # Set the thread as a daemon so it will exit when the main program exits
    # スレッドをdaemonにして、メインプログラムが終了したときに自動的に退出する
    input_thread.daemon = True

    # スレッドを開始する
    input_thread.start()
    
    # AVRCPのループを開始する
    GLib.MainLoop().run()

def debug_read_input():
    """
    コマンドラインにコマンドを入力して、デバッグを行う。
    使えるコマンドは、ジェスチャーセンサと同じコマンドである。
    
    コマンド: "left" "right" "up" "down" "clockwise" "anticlockwise" "wave"
    """
    while True:
        print("Enter gesture input: ")
        keyboardCommand = input()
        change_status(keyboardCommand)
  
def change_status(action):
    """
    入力が検出されたとき、入力に応じて処理を行う。

    Args:
        action (str): "up" "down" "left" "right" "clockwise" "anticlockwise" "wave"
    """
    
    print("Button pressed: " + str(action))
    
    # 今のステータスをチェック
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

    elif current_status == StatusEnum.MUSIC:
        if action == "down":
            arduino_control.change_status(StatusEnum.CLOCK)
        elif action == "right":
            playback_control("prev")
        elif action == "left":
            playback_control("next")

    # 任意のステータス
    if True:
        if action == "wave":
            playback_control("pp")
        elif action == "clockwise":
            playback_control("vol-up")
        elif action == "anticlockwise":
            playback_control("vol-down")

def on_property_changed(interface, changed, invalidated):
    """
    音楽情報に変更があるときに、自動的に実行される。

    """
    global playback_status
    global cacheAlbum, cacheArtist, cacheTitle
    if interface != 'org.bluez.MediaPlayer1':
        return
    for prop, value in changed.items():
        # もし変更がステータスの場合
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

        # もし変更が音楽情報の場合
        elif prop == 'Track':
            # デバッグ
            print('Music Info:')
            for key in ('Title', 'Artist', 'Album'):
                print('   {}: {}'.format(key, value.get(key, '')))

            # 変更されたタイトルとアーティスト
            changedTitle = value.get('Title', '')
            changedArtist = value.get('Artist', '')
            
            # Note: Some device will send title and artist first before album
            # アルバムを送信する前に先にタイトルと作家を送信するデバイスもあるので、タイトルが空白のときの対策もしておく
            if changedTitle != "" and cacheTitle != changedTitle:
                # 手前の音楽情報を消す
                arduino_control.avrcp_commands("artist", "Loading")
                arduino_control.avrcp_commands("title", "  ")
                arduino_control.avrcp_commands("cover", None)

                # 曲の画像を受け取る
                cover_art = get_and_process_album_art_web(changedTitle, changedArtist)
                if cover_art != None:
                    arduino_control.avrcp_commands("cover", str(cover_art))
                else:
                    arduino_control.avrcp_commands("cover")

            # 画像がアップロードされた後、音楽の情報を更新する
            if changedArtist != "":
                cacheArtist = changedArtist
                arduino_control.avrcp_commands("artist", changedArtist)
            if changedTitle != "":
                cacheTitle = changedTitle
                arduino_control.avrcp_commands("title", changedTitle)

    if 'Connected' in changed.get('org.bluez.Device1', {}):
        connected = changed['org.bluez.Device1']['Connected']
        if not connected:
            print("Bluetooth device is disconnected.")
            # You can add more actions here when the device is disconnected

def playback_control(command):
    """
    AVRCPコマンドを行い、デバイスの遠隔操作をする。

    Args:
        command (str): "play", "pause", "next", "prev", "vol-up", "vol-down", "pp" (playpause)

    Returns:
        bool: If success, True is returned.
    """
    str = command
    if str.startswith('play'):
        player_iface.Play()
    elif str.startswith('pause'):
        player_iface.Pause()
    elif str.startswith('pp'):
        if playback_status == "playing" or playback_status == "None":
            player_iface.Pause()
        elif playback_status == "paused" or playback_status == "None":
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
        currentLocalVol = mixer.getvolume()[0]
        print("currentLocalVol: " , currentLocalVol);
        addLocalVol = 0
        if (str == 'vol-up'):
            addLocalVol = 5
        elif (str == 'vol-down'):
            addLocalVol = -5
        newLocalVol = clamp(currentLocalVol + addLocalVol, 0 , 80)
        print("Local vol set:" , newLocalVol)
        mixer.setvolume(newLocalVol)
    return True

def get_and_process_album_art_web(title, artist):
    """
    インターネットから画像を検索し、1番目の検索結果を画像処理を行い、16ビットカラーの画像データをリストとして返す。

    Args:
        title (str): Song title.
        artist (str): Song artist.

    Returns:
        list: Image data in 16-bit format.
    """
    if title == '' or artist == '':
        print('Cannot fetch album art without title and artist information.')
        return None

    # 画像を検索する
    title = '"' + '+'.join(title.split()) + '"'
    artist = '"' + '+'.join(artist.split()) + '"'
    res = requests.get(URL+'+'.join((title, artist)), headers=HEADER)
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    img_tags = soup.find_all('img')
    image_url_list = [img['src'] for img in img_tags]

    # Googleロゴを除く1番目の検索結果の画像URLを用いる
    image_url = image_url_list[1]

    # 画像を処理する
    processed_image = process_image(image_url)
    if (processed_image is not None):
        pixel_values = list(processed_image.getdata())
        # 画像のデータはRGBAの32ビットカラーになっているため、まずはRGBの24ビットカラーに変換する
        pixel_data = [int(value) for pixel in pixel_values for value in pixel if pixel.index(value) % 4 != 3]
        cover_art = convert_to_16_bit(pixel_data)
        return cover_art
    else:
        return None
    
def convert_to_16_bit(input_data):
    """
    24ビットカラーを16ビットに変換する。

    Args:
        input_data (list): 24 bit color list.

    Raises:
        ValueError: Invalid value.

    Returns:
        list: 16 bit color list.
    """
    
    # Check if the input has a valid length
    # 入力が正しい長さを持っているかを検査する
    if len(input_data) % 3 != 0:
        raise ValueError("Input data length must be a multiple of 3 (representing RGB values).")

    # 8ビットRGBの値を16ビットRGBの値に変換する
    output_data = []
    for i in range(0, len(input_data), 3):
        r = input_data[i]
        g = input_data[i + 1]
        b = input_data[i + 2]

        # Combine the three 8-bit values into a single 16-bit value (5 bits for red, 6 bits for green, 5 bits for blue)
        # 三つの8ビットの値を一つの16ビットの値に統合させる (R: 5 bit, G: 6 bit, B: 5 bit)
        rgb_16_bit = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        
        output_data.append(rgb_16_bit)

    return output_data

def process_image(image_url):
    """インターネットから画像URLを用いて画像をダウンロードしてから32x32に調整する。

    Args:
        image_url (str): URL of the image.

    Returns:
        Image: Resized image of size 32x32.
    """
    if not image_url:
        print('Image URL not available.')
        return None

    response = requests.get(image_url)
    if response.status_code == 200:
        with open('album_art.jpg', 'wb') as f:
            f.write(response.content)

        # ダウンロードされた画像を開く
        original_image = Image.open('album_art.jpg')

        # 画像のサイズを32x32に調整する
        resized_image = original_image.resize((32, 32))
        resized_image.convert("RGB")
        resized_image.save("test.bmp")
        
        return resized_image
    else:
        print('Failed to download image. Status Code:', response.status_code)
        return None

def clamp(n, minn, maxn):
    """
    数字を範囲内に限定する

    Args:
        n (int): number
        minn (int): minimum
        maxn (int): maximum

    Returns:
        int: clamped
    """
    return max(min(maxn, n), minn)

# main()関数を呼び出す
if __name__ == "__main__":
    main() 
