from dataclasses import asdict, dataclass
from enum import Enum
from typing import List, Literal, Self, Tuple, Type

KeyPress = (
    Literal[0x01]
    | Literal[0x02]
    | Literal[0x04]
    | Literal[0x08]
    | Literal[0x10]
    | Literal[0x20]
)

KP_UP: KeyPress = 0x01
KP_ENTER: KeyPress = 0x02
KP_EXIT: KeyPress = 0x04
KP_LEFT: KeyPress = 0x08
KP_RIGHT: KeyPress = 0x10
KP_DOWN: KeyPress = 0x20


def keypress_repr(keypress: KeyPress) -> str:
    return {
        KP_UP: "KP_UP",
        KP_ENTER: "KP_ENTER",
        KP_EXIT: "KP_EXIT",
        KP_LEFT: "KP_LEFT",
        KP_RIGHT: "KP_RIGHT",
        KP_DOWN: "KP_DOWN",
    }[keypress]


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

    keypress: KeyPress
    pressed: bool
    pressed_since: bool
    released_since: bool

    @classmethod
    def from_bytes(cls: Type[Self], state: bytes, keypress: KeyPress) -> Self:
        pressed = state[0]
        pressed_since = state[1]
        released_since = state[2]

        return cls(
            keypress=keypress,
            pressed=bool(pressed & keypress),
            pressed_since=bool(pressed_since & keypress),
            released_since=bool(released_since & keypress),
        )

    def to_bytes(self: Self) -> Tuple[int, int, int]:
        pressed = self.keypress if self.pressed else 0x00
        pressed_since = self.keypress if self.pressed_since else 0x00
        released_since = self.keypress if self.released_since else 0x00

        return (pressed, pressed_since, released_since)


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
        return cls(
            up=KeyState.from_bytes(state, KP_UP),
            enter=KeyState.from_bytes(state, KP_ENTER),
            exit=KeyState.from_bytes(state, KP_EXIT),
            left=KeyState.from_bytes(state, KP_LEFT),
            right=KeyState.from_bytes(state, KP_RIGHT),
            down=KeyState.from_bytes(state, KP_DOWN),
        )

    def to_bytes(self: Self) -> bytes:
        pressed = 0x00
        pressed_since = 0x00
        released_since = 0x00

        for state in [
            self.up,
            self.enter,
            self.exit,
            self.left,
            self.right,
            self.down,
        ]:
            p, p_s, r_s = state.to_bytes()
            pressed = pressed ^ p
            pressed_since = pressed_since ^ p_s
            released_since = released_since ^ r_s

        return bytes([pressed, pressed_since, released_since])

    def __repr__(self: Self) -> str:
        repr_ = ""
        for name, state in asdict(self).items():
            st = ", ".join(
                [
                    (
                        f"{n}={'yes' if s else 'no'}"
                        if isinstance(s, bool)
                        else f"{n}={keypress_repr(s)}"
                    )
                    for n, s in state.items()
                ]
            )
            repr_ += f"{name}: {st}\n"
        return repr_[0:-1]


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
    def from_byte(cls: Type[Self], activity: int) -> "KeyActivity":
        return KEY_ACTIVITIES[activity - 1]

    @classmethod
    def from_bytes(cls: Type[Self], activity: bytes) -> "KeyActivity":
        return cls.from_byte(activity[0])

    def to_byte(self: Self) -> int:
        return self.value


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
