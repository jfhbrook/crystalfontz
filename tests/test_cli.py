import json
from typing import Any

import pytest

from crystalfontz.cli import as_json, parse_bytes

# from crystalfontz.device import CFA533Status
from crystalfontz.response import LcdMemory, Versions


@pytest.mark.parametrize(
    "text,buffer",
    [
        ("hello world", b"hello world"),
        ("\\\\", b"\\"),
        ("\\a", b"\a"),
        ("\\o333", (0o333).to_bytes(1, byteorder="big")),
        ("\\o22", (0o22).to_bytes(1, byteorder="big")),
        ("\\xff", b"\xff"),
        ("\\", b"\\"),
        ("\\s", b"\\s"),
        ("\\xf", b"\\xf"),
    ],
)
@pytest.mark.filterwarnings("ignore:invalid escape sequence")
def test_parse_bytes(text, buffer) -> None:
    assert parse_bytes(text) == buffer


OBJECTS = [
    Versions(b"CFA533: h1.4, u1v2"),
    LcdMemory(b"\xff\x00\x01\x02\x03\x04\x05\x06\x07"),
    # DowDeviceInformation(b""),
    # DowTransactionResult(b""),
    # KeypadPolled(b""),
    # CFA533Status(...),
    # GpioRead(b""),
]


@pytest.mark.parametrize("obj", OBJECTS)
def test_repr(obj: Any, snapshot) -> None:
    assert repr(obj) == snapshot


@pytest.mark.parametrize("obj", OBJECTS)
def test_json(obj: Any, snapshot) -> None:
    assert json.dumps(as_json(obj)) == snapshot
