import pytest

from crystalfontz.atx import AtxPowerSwitchFunction, AtxPowerSwitchFunctionalitySettings
from crystalfontz.device import CFA533, CFA533Status, Device, DeviceStatus
from crystalfontz.keys import KeyState, KeyStates

KEY_STATES = KeyStates(
    up=KeyState(pressed=False, pressed_since=False, released_since=False),
    enter=KeyState(pressed=True, pressed_since=False, released_since=False),
    exit=KeyState(pressed=False, pressed_since=True, released_since=False),
    left=KeyState(pressed=False, pressed_since=False, released_since=True),
    right=KeyState(pressed=True, pressed_since=True, released_since=False),
    down=KeyState(pressed=True, pressed_since=False, released_since=True),
)


ATX_SETTINGS = AtxPowerSwitchFunctionalitySettings(
    functions={AtxPowerSwitchFunction.KEYPAD_RESET},
    auto_polarity=True,
    reset_invert=False,
    power_invert=False,
    power_pulse_length_seconds=1.0,
)


@pytest.mark.parametrize(
    "device,status,size",
    [
        (
            CFA533(),
            CFA533Status(
                temperature_sensors_enabled={1, 2, 3},
                key_states=KEY_STATES,
                atx_power_switch_functionality_settings=ATX_SETTINGS,
                watchdog_counter=5,
                contrast=0.2,
                keypad_brightness=0.6,
                atx_sense_on_floppy=False,
                cfa633_contrast=0.2,
                lcd_brightness=0.3,
            ),
            15,
        )
    ],
)
def test_status_to_from_bytes(
    device: Device, status: DeviceStatus, size: int, snapshot
) -> None:
    as_bytes = status.to_bytes(device)

    assert len(as_bytes) == size
    assert as_bytes == snapshot

    from_bytes = status.__class__.from_bytes(as_bytes)

    assert from_bytes == status
