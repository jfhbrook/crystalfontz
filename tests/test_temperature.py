from typing import Set

import pytest

from crystalfontz.device import CFA533
from crystalfontz.temperature import (
    pack_temperature_settings,
    unpack_temperature_settings,
)


@pytest.mark.parametrize(
    "enabled,packed",
    [
        ({1, 9, 17, 25}, b"\x01\x01\x01\x01"),
        ({8, 16, 24, 32}, b"\x80\x80\x80\x80"),
        ({1, 2, 3, 4, 5, 6, 7, 8}, b"\xff\x00\x00\x00"),
    ],
)
def test_pack_temperature_settings(enabled: Set[int], packed: bytes) -> None:
    assert pack_temperature_settings(enabled, CFA533()) == packed


@pytest.mark.parametrize(
    "enabled,packed",
    [
        ({1, 9, 17, 25}, b"\x01\x01\x01\x01"),
        ({8, 16, 24, 32}, b"\x80\x80\x80\x80"),
        ({1, 2, 3, 4, 5, 6, 7, 8}, b"\xff\x00\x00\x00"),
    ],
)
def test_unpack_temperature_settings(enabled: Set[int], packed: bytes) -> None:
    assert unpack_temperature_settings(packed) == enabled
