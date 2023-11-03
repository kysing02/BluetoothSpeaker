import time
import rgbmatrix
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Set up the LED matrix
options = rgbmatrix.RGBMatrixOptions()
options.rows = 32
options.cols = 64
matrix = rgbmatrix.RGBMatrix(options=options)

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