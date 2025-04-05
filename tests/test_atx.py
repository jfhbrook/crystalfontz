import pytest

from crystalfontz.atx import AtxPowerSwitchFunction, AtxPowerSwitchFunctionalitySettings


@pytest.mark.parametrize(
    "settings",
    [
        AtxPowerSwitchFunctionalitySettings(
            functions={AtxPowerSwitchFunction.KEYPAD_RESET},
            auto_polarity=True,
            reset_invert=False,
            power_invert=False,
            power_pulse_length_seconds=1.0,
        )
    ],
)
def test_atx_settings_to_from_bytes(
    settings: AtxPowerSwitchFunctionalitySettings, snapshot
) -> None:
    as_bytes = settings.to_bytes()

    assert as_bytes == snapshot

    from_bytes = AtxPowerSwitchFunctionalitySettings.from_bytes(as_bytes)

    assert from_bytes == settings
