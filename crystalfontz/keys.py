from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Type

try:
    from typing import Self
except ImportError:
    Self = Any

KeyPress = int

KP_UP: KeyPress = 0x01
KP_ENTER: KeyPress = 0x02
KP_EXIT: KeyPress = 0x04
KP_LEFT: KeyPress = 0x08
KP_RIGHT: KeyPress = 0x10
KP_DOWN: KeyPress = 0x20


@dataclass
class KeyState:
    """
    A key's state.

    Attributes:
        pressed (bool): When True, the key is currently pressed.
        pressed_since (bool): When True, the key has been pressed since the last poll.
        released_since (bool): When True, the key has been released since the last
                               poll.
    """

    pressed: bool
    pressed_since: bool
    released_since: bool


@dataclass
class KeyStates:
    """
    The state of all keys.

    Attributes:
        up: The state of the "up" key.
        enter: The state of the "enter" key.
        exit: The state of the "exit" key.
        left: The state of the "left" key.
        right: The state of the "right" key.
        down: The state of the "down" key.
    """

    up: KeyState
    enter: KeyState
    exit: KeyState
    left: KeyState
    right: KeyState
    down: KeyState

    @classmethod
    def from_bytes(cls: Type[Self], state: bytes) -> Self:
        pressed = state[0]
        pressed_since = state[1]
        released_since = state[2]

        return cls(
            up=KeyState(
                pressed=bool(pressed & KP_UP),
                pressed_since=bool(pressed_since & KP_UP),
                released_since=bool(released_since & KP_UP),
            ),
            enter=KeyState(
                pressed=bool(pressed & KP_ENTER),
                pressed_since=bool(pressed_since & KP_ENTER),
                released_since=bool(released_since & KP_ENTER),
            ),
            exit=KeyState(
                pressed=bool(pressed & KP_EXIT),
                pressed_since=bool(pressed_since & KP_EXIT),
                released_since=bool(released_since & KP_EXIT),
            ),
            left=KeyState(
                pressed=bool(pressed & KP_LEFT),
                pressed_since=bool(pressed_since & KP_LEFT),
                released_since=bool(released_since & KP_LEFT),
            ),
            right=KeyState(
                pressed=bool(pressed & KP_RIGHT),
                pressed_since=bool(pressed_since & KP_RIGHT),
                released_since=bool(released_since & KP_RIGHT),
            ),
            down=KeyState(
                pressed=bool(pressed & KP_DOWN),
                pressed_since=bool(pressed_since & KP_DOWN),
                released_since=bool(released_since & KP_DOWN),
            ),
        )

    def as_dict(self: Self) -> Dict[str, Dict[str, bool]]:
        return {key: state for key, state in asdict(self).items()}


class KeyActivity(Enum):
    """
    A key activity. This is either a "press" event or a "release" event for a
    given key.
    """

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
    def from_bytes(cls: Type[Self], activity: bytes) -> "KeyActivity":
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
