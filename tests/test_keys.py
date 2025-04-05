from crystalfontz.keys import (
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
