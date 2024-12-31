import asyncio
from enum import Enum
from typing import Dict, List, Self, Type

from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE
from serial_asyncio import create_serial_connection, SerialTransport


class KeyActivity(Enum):
    KEY_UP_PRESS = 1
    KEY_DOWN_PRESS = 2
    KEY_LEFT_PRESS = 3
    KEY_RIGHT_PRESS = 4
    KEY_ENTER_PRESS = 5
    KEY_EXIT_PRESS = 6
    KEY_UP_RELEASE = 7
    KEY_DOWN_RELEASE = 8
    KEY_LEFT_RELEASE = 9
    KEY_RIGHT_RELEASE = 10
    KEY_ENTER_RELEASE = 11
    KEY_EXIT_RELEASE = 12

    @classmethod
    def from_bytes(cls, activity: bytes) -> "KeyActivity":
        return KEY_ACTIVITIES[activity[0] - 1]


KEY_ACTIVITIES: List[KeyActivity] = [
    KeyActivity.KEY_UP_PRESS,
    KeyActivity.KEY_DOWN_PRESS,
    KeyActivity.KEY_LEFT_PRESS,
    KeyActivity.KEY_RIGHT_PRESS,
    KeyActivity.KEY_ENTER_PRESS,
    KeyActivity.KEY_EXIT_PRESS,
    KeyActivity.KEY_UP_RELEASE,
    KeyActivity.KEY_DOWN_RELEASE,
    KeyActivity.KEY_LEFT_RELEASE,
    KeyActivity.KEY_RIGHT_RELEASE,
    KeyActivity.KEY_ENTER_RELEASE,
    KeyActivity.KEY_EXIT_RELEASE,
]
