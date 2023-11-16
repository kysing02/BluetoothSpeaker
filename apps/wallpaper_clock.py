import sys
sys.path.insert(0, '/home/student/BluetoothSpeaker')
import time
import sys
import asyncio
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from utils import display
from apps import clock, wallpaper

async def display_wallpaper_clock(value):
    '''
    Displays wallpaper + clock with given arguments.
    value: Select which wallpaper to be displayed (0-3). Select 0 for cached value
    '''
    asyncio.create_task(combine_wallpaper_clock_task(value))
    await asyncio.sleep(0)

async def combine_wallpaper_clock_task(value):
    task1 = asyncio.create_task(wallpaper.display_wallpaper(value, "half"))
    task2 = asyncio.create_task(clock.display_clock("half"))
    await asyncio.gather(task1, task2)

def change_wallpaper(value):
    '''
    Change wallpaper to be displayed. Set 1 to show next wallpaper or -1 to show previous wallpaper next time display_wallpaper() is invoked.
    '''
    wallpaper.change_wallpaper(value, "half")