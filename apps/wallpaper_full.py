#!/usr/bin/env python
import time
import json
import sys
from rgbmatrix import RGBMatrix
from PIL import Image
from utils import display

def display_wallpaper(value):
    image_file = "../images/wallpaper" + value + ".jpg"

    gif = Image.open(image_file)

    try:
        num_frames = gif.n_frames
    except Exception:
        sys.exit("provided image is not a gif")

    # Configuration for the matrix
    matrix = display.get_rgb_matrix()

    # Preprocess the gifs frames into canvases to improve playback performance
    canvases = []
    print("Preprocessing gif, this may take a moment depending on the size of the gif...")
    for frame_index in range(0, num_frames):
        gif.seek(frame_index)
        # must copy the frame out of the gif, since thumbnail() modifies the image in-place
        frame = gif.copy()
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