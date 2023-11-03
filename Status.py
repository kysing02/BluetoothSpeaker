# Note: This is a static class. No instance should be created.
from enum import Enum

# Flags for stopping and blocking threads

# Status Enum for tracking status
class StatusEnum(Enum):
    SLEEP = 0
    WALLPAPER_FULL = 1
    WALLPAPER_CLOCK = 2
    CLOCK_FULL = 3
    MUSIC = 4

class Status:
    # Initial status
    _status = StatusEnum.SLEEP

    @classmethod
    def set_status(cls, status_enum):
        cls.status = status_enum

    @classmethod
    def get_status(cls):
        return cls.status