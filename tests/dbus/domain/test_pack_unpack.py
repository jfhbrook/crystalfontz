from typing import Any, Callable, cast, Optional, Type

import pytest

from crystalfontz.baud import FAST_BAUD_RATE, SLOW_BAUD_RATE
from crystalfontz.config import Config
from crystalfontz.cursor import CursorStyle
from crystalfontz.dbus.domain.atx import (
    AtxPowerSwitchFunction,
    AtxPowerSwitchFunctionalitySettingsM,
)
from crystalfontz.dbus.domain.base import (
    BytesM,
    OptBytesM,
    OptFloatM,
    OptIntM,
    RetryTimesM,
    TimeoutM,
)
from crystalfontz.dbus.domain.baud import BaudRateM
from crystalfontz.dbus.domain.config import ConfigM
from crystalfontz.dbus.domain.cursor import CursorStyleM
from crystalfontz.dbus.domain.device import DeviceM
from crystalfontz.dbus.domain.gpio import GpioSettingsM, OptGpioSettingsM
from crystalfontz.dbus.domain.keys import KeypadBrightnessM
from crystalfontz.dbus.domain.lcd import LcdRegisterM
from crystalfontz.device import lookup_device
from crystalfontz.gpio import GpioDriveMode, GpioFunction, GpioSettings
from crystalfontz.lcd import LcdRegister

ValidateFn = Callable[[Any, Any], None]


def validate_is(actual: Any, expected: Any) -> None:
    assert isinstance(actual, expected.__class__)


def validate_gpio_settings(actual: Any, expected: Any) -> None:
    if expected is None:
        assert actual is None
        return
    assert actual.function == expected.function
    assert actual.mode == expected.mode


@pytest.mark.parametrize(
    "entity,map_cls,validate",
    [
        (1, OptIntM, None),
        (None, OptIntM, None),
        (1.0, OptFloatM, None),
        (None, OptFloatM, None),
        (b"hello", BytesM, None),
        (b"hello", OptBytesM, None),
        (None, OptBytesM, None),
        (1.0, TimeoutM, None),
        (None, TimeoutM, None),
        (1, RetryTimesM, None),
        (None, RetryTimesM, None),
        (
            cast(Any, Config)(
                file="/etc/crystalfontz.yaml",
                port="/dev/ttyUSB1",
                model="CFA533",
                hardware_rev="h1.4",
                firmware_rev="u1v2",
                baud_rate=FAST_BAUD_RATE,
                timeout=0.250,
                retry_times=1,
            ),
            ConfigM,
            None,
        ),
        (CursorStyle.BLINKING_UNDERSCORE, CursorStyleM, None),
        (lookup_device("CFA533", "h1.4", "u1v2"), DeviceM, validate_is),
        (
            GpioSettings(
                function=GpioFunction.UNUSED,
                up=GpioDriveMode.FAST_STRONG,
                down=GpioDriveMode.RESISTIVE,
            ),
            GpioSettingsM,
            validate_gpio_settings,
        ),
        (
            GpioSettings(
                function=GpioFunction.UNUSED,
                up=GpioDriveMode.FAST_STRONG,
                down=GpioDriveMode.RESISTIVE,
            ),
            OptGpioSettingsM,
            validate_gpio_settings,
        ),
        (
            None,
            OptGpioSettingsM,
            validate_gpio_settings,
        ),
        (1.0, KeypadBrightnessM, None),
        (None, KeypadBrightnessM, None),
        (LcdRegister.DATA, LcdRegisterM, None),
        (LcdRegister.CONTROL, LcdRegisterM, None),
    ],
)
def test_domain_pack_unpack(
    entity: Any, map_cls: Any, validate: Optional[ValidateFn], snapshot
) -> None:
    packed = map_cls.pack(entity)

    assert packed == snapshot

    if hasattr(map_cls, "unpack"):
        unpacked = map_cls.unpack(packed)
        if validate:
            validate(unpacked, entity)
        else:
            assert unpacked == entity


@pytest.mark.parametrize(
    "packed,map_cls",
    [
        ([], OptBytesM),
        (
            ([AtxPowerSwitchFunction.KEYPAD_RESET.value], False, True, True, 1.0),
            AtxPowerSwitchFunctionalitySettingsM,
        ),
        (SLOW_BAUD_RATE, BaudRateM),
        (FAST_BAUD_RATE, BaudRateM),
    ],
)
def test_domain_unpack_pack(packed: Any, map_cls: Any, snapshot) -> None:
    entity = map_cls.unpack(packed)

    assert entity == snapshot

    if hasattr(map_cls, "pack"):
        repacked = map_cls.pack(entity)
        assert repacked == packed


@pytest.mark.parametrize("packed,map_cls,exc_cls", [(12, BaudRateM, ValueError)])
def test_domain_unpack_error(
    packed: Any, map_cls: Any, exc_cls: Type[Exception]
) -> None:
    with pytest.raises(exc_cls):
        map_cls.unpack(packed)
