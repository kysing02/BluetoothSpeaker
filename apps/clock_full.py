import time
from PIL import ImageDraw
from PIL import ImageFont
from utils import display

def display_clock_full():
    '''
    Display clock.
    '''
    
    # Set up the LED matrix
    matrix = display.get_rgb_matrix()

    # Create a canvas for the right half of the matrix 
    matrix = matrix.CreateFrameCanvas()

    while True:
        display_clock(matrix)
        matrix = matrix.SwapOnVSync(matrix)
        
# Create a function to display the clock on the right half
def display_clock(canvas):
    font = ImageFont.load_default()
    draw = ImageDraw.Draw(canvas)
    draw.text((0, 16), time.strftime("%H:%M:%S"), fill=(255, 255, 255), font=font)