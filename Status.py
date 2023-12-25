# Note: This is a static class. No instance should be created.
from enum import Enum

# Status Enum for tracking status
class StatusEnum(Enum):
    SLEEP = 0
    CLOCK = 1
    WALLPAPER_CLOCK = 2
    MUSIC = 3

class Status:
    # Initial status
    _status = StatusEnum.SLEEP
    _persistent_status = StatusEnum.CLOCK
    @classmethod
    def set_status(cls, status_enum):
        cls._status = status_enum

    @classmethod
    def get_status(cls):
        return cls._status

    @classmethod
    def set_persistent_status(cls):
        cls._persistent_status = cls._status

    @classmethod
    def get_persistent_status(cls):
        return cls._persistent_status