import time
import json
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from rgbmatrix import RGBMatrixOptions, RGBMatrix

# Set up the LED matrix
config = json.load("config.json")
options = RGBMatrixOptions()
options.rows = config['display_rows']
options.cols = config['display_columns']
matrix = RGBMatrix(options=options)

# Create a canvas for the right half of the matrix 
matrix = matrix.CreateFrameCanvas()

# Create a function to display the clock on the right half
def display_clock(canvas):
    font = ImageFont.load_default()
    draw = ImageDraw.Draw(canvas)
    draw.text((0, 16), time.strftime("%H:%M:%S"), fill=(255, 255, 255), font=font)

try:
    while True:
        display_clock(matrix)
        matrix = matrix.SwapOnVSync(matrix)
except KeyboardInterrupt:
    matrix.Clear()