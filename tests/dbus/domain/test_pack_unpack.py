from typing import Any, Callable, Optional, Type

import pytest

from crystalfontz.baud import FAST_BAUD_RATE, SLOW_BAUD_RATE
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

ValidateFn = Callable[[Any, Any], None]


def validate_eq(actual: Any, expected: Any) -> None:
    assert actual == expected


def validate_is(actual: Any, expected: Any) -> None:
    assert isinstance(actual, expected.__class__)


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
