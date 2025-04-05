from typing import Set

import pytest

from crystalfontz.device import CFA533, Device
from crystalfontz.temperature import (
    pack_temperature_settings,
    unpack_temperature_settings,
)


@pytest.mark.parametrize("enabled,device", [({1, 2, 3}, CFA533())])
def test_status_to_from_bytes(enabled: Set[int], device: Device, snapshot) -> None:
    as_bytes = pack_temperature_settings(enabled, device)

    assert as_bytes == snapshot

    from_bytes = unpack_temperature_settings(as_bytes)

    assert from_bytes == enabled
