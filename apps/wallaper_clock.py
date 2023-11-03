import time
import json
import sys
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from rgbmatrix import RGBMatrix
from utils import display

# Set up the LED matrix
matrix = display.get_rgb_matrix()

# Load and display the GIF on the left half of the matrix
left_half_matrix = matrix.CreateFrameCanvas()
left_gif = Image.open("left_half.gif")

try:
    num_frames = left_gif.n_frames
except Exception:
    sys.exit("provided image is not a gif")

left_half_matrix.SetImage(left_gif.convert('RGB'), 0, 0)
left_half_matrix = matrix.SwapOnVSync(left_half_matrix)

# Create a canvas for the right half of the matrix 
right_half_matrix = matrix.CreateFrameCanvas()

# Create a function to display the clock on the right half
def display_clock(canvas):
    font = ImageFont.load_default()
    draw = ImageDraw.Draw(canvas)
    draw.text((32, 16), time.strftime("%H:%M:%S"), fill=(255, 255, 255), font=font)

try:
    while True:
        display_clock(right_half_matrix)
        right_half_matrix = matrix.SwapOnVSync(right_half_matrix)
except KeyboardInterrupt:
    matrix.Clear()