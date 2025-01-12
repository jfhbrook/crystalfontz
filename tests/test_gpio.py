import pytest

from crystalfontz.gpio import GpioDriveMode, GpioFunction, GpioSettings


def _expected(fn: GpioFunction, mode: int) -> int:
    return mode + (0b1000 if fn == GpioFunction.USED else 0)


@pytest.mark.parametrize(
    "settings,encoded",
    [
        test_case
        for fn in [GpioFunction.UNUSED, GpioFunction.USED]
        for test_case in [
            (
                GpioSettings(
                    fn,
                    up=GpioDriveMode.FAST_STRONG,
                    down=GpioDriveMode.RESISTIVE,
                ),
                _expected(fn, 0b000),
            ),
            (
                GpioSettings(
                    fn,
                    up=GpioDriveMode.FAST_STRONG,
                    down=GpioDriveMode.FAST_STRONG,
                ),
                _expected(fn, 0b001),
            ),
            (
                GpioSettings(
                    fn,
                    up=GpioDriveMode.HI_Z,
                    down=None,
                ),
                _expected(fn, 0b010),
            ),
            (
                GpioSettings(
                    fn,
                    up=GpioDriveMode.RESISTIVE,
                    down=GpioDriveMode.FAST_STRONG,
                ),
                _expected(fn, 0b011),
            ),
            (
                GpioSettings(
                    fn,
                    up=GpioDriveMode.SLOW_STRONG,
                    down=GpioDriveMode.HI_Z,
                ),
                _expected(fn, 0b100),
            ),
            (
                GpioSettings(
                    fn,
                    up=GpioDriveMode.SLOW_STRONG,
                    down=GpioDriveMode.SLOW_STRONG,
                ),
                _expected(fn, 0b101),
            ),
            (
                GpioSettings(
                    fn,
                    up=GpioDriveMode.HI_Z,
                    down=GpioDriveMode.SLOW_STRONG,
                ),
                _expected(fn, 0b111),
            ),
        ]
    ],
)
def test_gpio_settings(settings: GpioSettings, encoded: int) -> None:
    assert settings.to_bytes() == encoded.to_bytes(1, "big")
