from crystalfontz.keys import KeyState, KeyStates


def test_key_states_to_from_bytes(snapshot) -> None:
    key_states = KeyStates(
        up=KeyState(pressed=False, pressed_since=False, released_since=False),
        enter=KeyState(pressed=True, pressed_since=False, released_since=False),
        exit=KeyState(pressed=False, pressed_since=True, released_since=False),
        left=KeyState(pressed=False, pressed_since=False, released_since=True),
        right=KeyState(pressed=True, pressed_since=True, released_since=False),
        down=KeyState(pressed=True, pressed_since=False, released_since=True),
    )

    as_bytes = key_states.to_bytes()

    assert as_bytes == snapshot

    from_bytes = KeyStates.from_bytes(as_bytes)

    assert from_bytes == key_states
