import time
import asyncio
from PIL import ImageDraw
from PIL import ImageFont
from utils import display

async def display_clock(size="full"):
    '''
    Display clock.
    size: Select what size to be displayed ("half" or "full")
    '''
    
    # Set up the LED matrix
    matrix = display.get_rgb_matrix()

    # Create a canvas for the right half of the matrix 
    matrix = matrix.CreateFrameCanvas()

    while True:
        draw_clock(matrix, size)
        matrix = matrix.SwapOnVSync(matrix)
        asyncio.sleep(0)
        
# Create a function to display the clock on the right half
def draw_clock(canvas, size):
    font = ImageFont.load_default()
    draw = ImageDraw.Draw(canvas)
    if size == "half":
        draw.text((16, 16), time.strftime("%H:%M:%S"), fill=(255, 255, 255), font=font)
    elif size == "full":
        draw.text((32, 16), time.strftime("%H:%M:%S"), fill=(255, 255, 255), font=font)