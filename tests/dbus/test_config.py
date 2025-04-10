from typing import Any, cast

import pytest

from crystalfontz.baud import FAST_BAUD_RATE, SLOW_BAUD_RATE
from crystalfontz.config import Config, GLOBAL_FILE

try:
    from crystalfontz.dbus.config import StagedConfig
except ImportError:
    StagedConfig = None

cfg_cls = cast(Any, Config)


@pytest.mark.parametrize(
    "active_config,target_config",
    [
        (
            cfg_cls(
                file=GLOBAL_FILE,
                port="/dev/ttyS0",
                model="CFA533",
                hardware_rev="h1.4",
                firmware_rev="u1v2",
                baud_rate=FAST_BAUD_RATE,
                timeout=0.250,
                retry_times=1,
            ),
            cfg_cls(
                file=GLOBAL_FILE,
                port="/dev/ttyS0",
                model="CFA533",
                hardware_rev="h1.4",
                firmware_rev="u1v2",
                baud_rate=FAST_BAUD_RATE,
                timeout=0.250,
                retry_times=1,
            ),
        ),
        (
            cfg_cls(
                file=GLOBAL_FILE,
                port="/dev/ttyS0",
                model="CFA533",
                hardware_rev="h1.4",
                firmware_rev="u1v2",
                baud_rate=FAST_BAUD_RATE,
                timeout=0.250,
                retry_times=1,
            ),
            cfg_cls(
                file=GLOBAL_FILE,
                port="/dev/ttyS4",
                model="CFA533",
                hardware_rev="h1.4",
                firmware_rev="u1v2",
                baud_rate=SLOW_BAUD_RATE,
                timeout=0.250,
                retry_times=1,
            ),
        ),
    ],
)
def test_staged_config_as_dict(active_config, target_config, snapshot) -> None:
    cls = cast(Any, StagedConfig)
    staged = cls(active_config=active_config, target_config=target_config)
    assert staged.as_dict() == snapshot


@pytest.mark.parametrize(
    "active_config,target_config",
    [
        (
            cfg_cls(
                file=GLOBAL_FILE,
                port="/dev/ttyS0",
                model="CFA533",
                hardware_rev="h1.4",
                firmware_rev="u1v2",
                baud_rate=FAST_BAUD_RATE,
                timeout=0.250,
                retry_times=1,
            ),
            cfg_cls(
                file=GLOBAL_FILE,
                port="/dev/ttyS0",
                model="CFA533",
                hardware_rev="h1.4",
                firmware_rev="u1v2",
                baud_rate=FAST_BAUD_RATE,
                timeout=0.250,
                retry_times=1,
            ),
        ),
        (
            cfg_cls(
                file=GLOBAL_FILE,
                port="/dev/ttyS0",
                model="CFA533",
                hardware_rev="h1.4",
                firmware_rev="u1v2",
                baud_rate=FAST_BAUD_RATE,
                timeout=0.250,
                retry_times=1,
            ),
            cfg_cls(
                file=GLOBAL_FILE,
                port="/dev/ttyS4",
                model="CFA533",
                hardware_rev="h1.4",
                firmware_rev="u1v2",
                baud_rate=SLOW_BAUD_RATE,
                timeout=0.250,
                retry_times=1,
            ),
        ),
    ],
)
def test_staged_config_repr(active_config, target_config, snapshot) -> None:
    cls = cast(Any, StagedConfig)
    staged = cls(active_config=active_config, target_config=target_config)
    assert repr(staged) == snapshot
