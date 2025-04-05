import pytest

from crystalfontz.keys import (
    KeyActivity,
    KeyState,
    KeyStates,
    KP_DOWN,
    KP_ENTER,
    KP_EXIT,
    KP_LEFT,
    KP_RIGHT,
    KP_UP,
)


def test_key_states_to_from_bytes(snapshot) -> None:
    key_states = KeyStates(
        up=KeyState(
            keypress=KP_UP, pressed=False, pressed_since=False, released_since=False
        ),
        enter=KeyState(
            keypress=KP_ENTER, pressed=True, pressed_since=False, released_since=False
        ),
        exit=KeyState(
            keypress=KP_EXIT, pressed=False, pressed_since=True, released_since=False
        ),
        left=KeyState(
            keypress=KP_LEFT, pressed=False, pressed_since=False, released_since=True
        ),
        right=KeyState(
            keypress=KP_RIGHT, pressed=True, pressed_since=True, released_since=False
        ),
        down=KeyState(
            keypress=KP_DOWN, pressed=True, pressed_since=False, released_since=True
        ),
    )

    as_bytes = key_states.to_bytes()

    assert as_bytes == snapshot

    from_bytes = KeyStates.from_bytes(as_bytes)

    assert from_bytes == key_states


@pytest.mark.parametrize(
    "activity",
    [
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
    ],
)
def test_key_activity_to_from_byte(activity: KeyActivity) -> None:
    byte = activity.to_byte()
    from_byte = KeyActivity.from_byte(byte)

    assert from_byte == activity
