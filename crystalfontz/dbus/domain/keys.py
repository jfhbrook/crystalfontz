from typing import ClassVar, Set, Tuple

from crystalfontz.dbus.domain.base import ByteM, OptFloatM, OptFloatT, struct
from crystalfontz.keys import (
    KeyActivity,
    KeyPress,
    KeyState,
    KeyStates,
    KP_DOWN,
    KP_ENTER,
    KP_EXIT,
    KP_LEFT,
    KP_RIGHT,
    KP_UP,
)

KeyPressT = int

KEYPRESSES: Set[KeyPress] = {KP_UP, KP_ENTER, KP_EXIT, KP_LEFT, KP_RIGHT, KP_DOWN}


class KeyPressM(ByteM):
    t: ClassVar[str] = ByteM.t

    @staticmethod
    def unpack(keypress: int) -> KeyPress:
        if keypress not in KEYPRESSES:
            raise ValueError(f"{keypress} is not a valid key press")
        return keypress


KeyStateT = Tuple[bool, bool, bool]
KeyStatesT = Tuple[
    KeyStateT,
    KeyStateT,
    KeyStateT,
    KeyStateT,
    KeyStateT,
    KeyStateT,
]


class KeyStateM:
    t: ClassVar[str] = struct("bbb")

    @staticmethod
    def pack(state: KeyState) -> KeyStateT:
        return (state.pressed, state.pressed_since, state.released_since)

    @staticmethod
    def unpack(state: KeyStateT, keypress: KeyPress) -> KeyState:
        pressed, pressed_since, released_since = state
        return KeyState(
            keypress=keypress,
            pressed=pressed,
            pressed_since=pressed_since,
            released_since=released_since,
        )


class KeyStatesM:
    t: ClassVar[str] = struct(KeyStateM.t) * 6

    @staticmethod
    def pack(states: KeyStates) -> KeyStatesT:
        return (
            KeyStateM.pack(states.up),
            KeyStateM.pack(states.enter),
            KeyStateM.pack(states.exit),
            KeyStateM.pack(states.left),
            KeyStateM.pack(states.right),
            KeyStateM.pack(states.down),
        )

    @staticmethod
    def unpack(states: KeyStatesT) -> KeyStates:
        up, enter, exit, left, right, down = states
        return KeyStates(
            up=KeyStateM.unpack(up, KP_UP),
            enter=KeyStateM.unpack(enter, KP_ENTER),
            exit=KeyStateM.unpack(exit, KP_EXIT),
            left=KeyStateM.unpack(left, KP_LEFT),
            right=KeyStateM.unpack(right, KP_RIGHT),
            down=KeyStateM.unpack(down, KP_DOWN),
        )


KeypadBrightnessT = OptFloatT


class KeypadBrightnessM(OptFloatM):
    """
    Map `Optional[float]` to and from `KeypadBrightnessT` (`float`).

    `KeypadBrightnessM` is an alias for `OptFloatM`.
    """

    t: ClassVar[str] = OptFloatM.t


KeyActivityT = int


class KeyActivityM:
    """
    Map `KeyActivity` to and from `KeyActivityT` (`int`).
    """

    t: ClassVar[str] = ByteM.t

    @staticmethod
    def pack(activity: KeyActivity) -> KeyActivityT:
        return activity.to_byte()

    @staticmethod
    def unpack(activity: KeyActivityT) -> KeyActivity:
        return KeyActivity.from_byte(activity)
