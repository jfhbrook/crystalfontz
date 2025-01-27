from typing import Any

import pytest

from crystalfontz.baud import FAST_BAUD_RATE
from crystalfontz.config import Config, GLOBAL_FILE


@pytest.fixture
def config() -> Config:
    return Config(file=GLOBAL_FILE)


@pytest.mark.parametrize(
    "name",
    [
        "port",
        "model",
        "hardware_rev",
        "firmware_rev",
        "baud_rate",
        "timeout",
        "retry_times",
    ],
)
def test_get(config: Config, name: str) -> None:
    assert config.get(name) == getattr(config, name)


def test_get_unknown(config: Config) -> None:
    with pytest.raises(ValueError):
        config.get("pony")


@pytest.mark.parametrize(
    "name,value,expected",
    [
        ("port", "/dev/ttyUSB1", "/dev/ttyUSB1"),
        ("model", "some_model", "some_model"),
        ("hardware_rev", "1.2.3", "1.2.3"),
        ("firmware_rev", "1.2.3", "1.2.3"),
        ("baud_rate", str(FAST_BAUD_RATE), FAST_BAUD_RATE),
        ("timeout", "1.2", 1.2),
        ("retry_times", "5", 5),
    ],
)
def test_set(config: Config, name: str, value: str, expected: Any) -> None:
    config.set(name, value)
    assert config.get(name) == expected


@pytest.mark.parametrize(
    "name,value",
    [
        ("baud_rate", "100"),
        (
            "retry_times",
            "5.5",
        ),
    ],
)
def test_set_value_error(config: Config, name: str, value: str) -> None:
    with pytest.raises(ValueError):
        config.set(name, value)


def test_set_unknown(config: Config) -> None:
    with pytest.raises(ValueError):
        config.set("pony", "pony")


@pytest.mark.parametrize("name", ["hardware_rev", "firmware_rev"])
def test_unset(config: Config, name: str) -> None:
    config.unset(name)
    assert config.get(name) is None


@pytest.mark.parametrize("name", ["port", "model", "baud_rate"])
def test_unset_required(config: Config, name: str) -> None:
    with pytest.raises(ValueError):
        config.unset(name)


def test_repr(config: Config, snapshot) -> None:
    assert repr(config) == snapshot
