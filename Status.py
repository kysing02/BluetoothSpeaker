"""
This is status program that keep tracks with current status and get status enum defined.

このプログラムは主にラズパイの内部ステータス（モード）を追跡するためのプログラムである。

"""

# Note: 
from enum import Enum

# Status Enum for tracking status
class StatusEnum(Enum):
    """
    Status that is defined.
    
    定義済みのステータスの集合クラス。
    """
    SLEEP = 0
    CLOCK = 1
    WALLPAPER_CLOCK = 2
    MUSIC = 3
    WEATHER = 4

class Status:
    """
    Note: This is a static class. No instance should be created.

    このクラスはstaticクラスである。インスタンスを作ることができない。
    """
    # Initial status（初期状態）
    _status = StatusEnum.SLEEP
    _persistent_status = StatusEnum.CLOCK
    
    @classmethod
    def set_status(cls, status_enum):
        """Set status.

        Args:
            status_enum (StatusEnum): StatusEnum to set.
        """
        cls._status = status_enum

    @classmethod
    def get_status(cls):
        """Get current status.

        Returns:
            StatusEnum: Current StatusEnum.
        """
        return cls._status

    # Persistent statusはステータスが変更されたとき、手前のステータスを記憶しておくために使われている。
    
    @classmethod
    def set_persistent_status(cls):
        """Set persistent status.

        Args:
            status_enum (StatusEnum): StatusEnum to set.
        """
        cls._persistent_status = cls._status

    @classmethod
    def get_persistent_status(cls):
        """Get current persistent status.

        Returns:
            StatusEnum: Current persistent StatusEnum.
        """
        return cls._persistent_status