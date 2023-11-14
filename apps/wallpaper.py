#!/usr/bin/env python
import sys
import io
import asyncio
from PIL import Image
from utils import display

current_full_image = 1
current_half_image = 1

matrix = display.get_rgb_matrix()
    
async def display_wallpaper(value=0, size="full"):
    '''
    Displays wallpaper with given arguments.
    value: Select which wallpaper to be displayed (0-3). Select 0 for cached value.
    size: Select what size to be displayed ("half" or "full")
    '''
    print("Displaying wallpaper...")
    # Check input
    if (size == "half"):
        # If cached wallpaper is selected
        if value == 0:
            # Set value to cached wallpaper
            value = current_half_image
        else:
            # Set cached wallpaper to specified value
            current_half_image = value
    elif (size == "full"):
        if value == 0:
            value = current_full_image
        else:
            current_full_image = value
    else:
        print("Error: Invalid argument size is provided.")
        return
    
    # TODO Add GIF Cycle Mode
    image_file = "../images/wallpapers/" + str(size) + "/wallpaper" + str(value) + ".gif"

    gif = Image.open(image_file)

    try:
        num_frames = gif.n_frames
    except Exception:
        sys.exit("provided image is not a gif")

    # Preprocess the gifs frames into canvases to improve playback performance
    canvases = []
    print("Preprocessing gif, this may take a moment depending on the size of the gif...")
    for frame_index in range(0, num_frames):
        gif.seek(frame_index)
        # must copy the frame out of the gif, since thumbnail() modifies the image in-place
        frame = gif.copy()
        if size == "half":
            frame.thumbnail((matrix.width/2, matrix.height), Image.ANTIALIAS)
        elif size == "full":
            frame.thumbnail((matrix.width, matrix.height), Image.ANTIALIAS)
        canvas = matrix.CreateFrameCanvas()
        canvas.SetImage(frame.convert("RGB"))
        canvases.append(canvas)
    # Close the gif file to save memory now that we have copied out all of the frames
    gif.close()

    print("Completed Preprocessing, displaying gif")

    # Infinitely loop through the gif
    cur_frame = 0
    while(True):
        matrix.SwapOnVSync(canvases[cur_frame], framerate_fraction=10)
        if cur_frame == num_frames - 1:
            cur_frame = 0
        else:
            cur_frame += 1
        asyncio.sleep(0)

def change_wallpaper(value, size="full"):
    '''
    Change wallpaper to be displayed. Set 1 to show next wallpaper or -1 to show previous wallpaper next time display_wallpaper() is invoked.
    '''
    print("Wallpaper changed")
    if size == "full":
        current_full_image = (current_full_image + value) % 3
        if current_full_image == 0:
            current_full_image = 3
    elif size == "half":
        current_half_image = (current_half_image + value) % 3
        if current_half_image == 0:
            current_half_image = 3
    
def save_wallpaper(value, size, data):
    image = bytes_to_gif(data)
    image_save_path = "../images/wallpapers/" + str(size) + "/wallpaper" + str(value) + ".gif"
    image.save(image_save_path)

def bytes_to_gif(byte_data):
    try:
        image = Image.open(io.BytesIO(byte_data))
        return image
    except Exception as e:
        print("Error converting bytes to GIF:", e)
        return None

def gif_to_bytes(image):
    try:
        output = io.BytesIO()
        image.save(output, format="GIF")
        return output.getvalue()
    except Exception as e:
        print("Error converting GIF to bytes:" + e)
        return None