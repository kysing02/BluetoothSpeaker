import time
import sys
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from utils import display

def display_wallpaper_clock(value):
    '''
    Displays wallpaper + clock with given arguments.
    value: Select which wallpaper to be displayed (1-3)
    '''
    # TODO Add GIF Cycle Mode
    image_file = "../images/wallpapers/half/wallpaper" + value + ".gif"

    gif = Image.open(image_file)

    try:
        num_frames = gif.n_frames
    except Exception:
        sys.exit("provided image is not a gif")
        
    # Set up the LED matrix
    matrix = display.get_rgb_matrix()

    # 1. Create left canvas
    
    left_matrix = matrix

    # Preprocess the gifs frames into canvases to improve playback performance
    canvases = []
    print("Preprocessing gif, this may take a moment depending on the size of the gif...")
    for frame_index in range(0, num_frames):
        gif.seek(frame_index)
        # must copy the frame out of the gif, since thumbnail() modifies the image in-place
        frame = gif.copy()
        frame.thumbnail((left_matrix.width / 2, left_matrix.height), Image.ANTIALIAS)
        canvas = left_matrix.CreateFrameCanvas()
        canvas.SetImage(frame.convert("RGB"))
        canvases.append(canvas)
    # Close the gif file to save memory now that we have copied out all of the frames
    gif.close()

    print("Completed Preprocessing")

    # 2. Create right canvas
    
    right_matrix = matrix.CreateFrameCanvas()
    
    # Infinitely loop through the gif and clock
    cur_frame = 0
    while True:
        # Clock
        display_clock(right_matrix)
        right_matrix = matrix.SwapOnVSync(right_matrix)

        # GIF
        left_matrix.SwapOnVSync(canvases[cur_frame], framerate_fraction=10)
        if cur_frame == num_frames - 1:
            cur_frame = 0
        else:
            cur_frame += 1

# Display the clock on the right half
def display_clock(canvas):
    font = ImageFont.load_default()
    draw = ImageDraw.Draw(canvas)
    draw.text((32, 16), time.strftime("%H:%M:%S"), fill=(255, 255, 255), font=font)