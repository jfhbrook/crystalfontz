from abc import ABC, abstractmethod
import struct
from typing import Dict, Self, Type

from crystalfontz.error import DecodeError, DeviceError, UnknownResponseError
from crystalfontz.keys import KeyActivity
from crystalfontz.packet import Packet


def assert_empty(data: bytes) -> None:
    if len(data) != 0:
        raise DecodeError("Response expected to be 0 bytes, is {len(data)} bytes")


def assert_len(n: int, data: bytes) -> None:
    if len(data) != n:
        raise DecodeError(f"Response expected to be {n} bytes, is {len(data)} bytes")


class Response(ABC):
    """
    A response received from the Crystalfontz LCD.
    """

    @abstractmethod
    def __init__(self, data: bytes) -> None:
        raise NotImplementedError("__init__")

    @classmethod
    def from_packet(cls: Type[Self], packet: Packet) -> "Response":
        code, data = packet
        if code in RESPONSE_CLASSES:
            return RESPONSE_CLASSES[code](data)

        if DeviceError.is_error_code(code):
            raise DeviceError(packet)

        raise UnknownResponseError(packet)


class Pong(Response):
    def __init__(self: Self, data: bytes) -> None:
        self.response = data

    def __str__(self: Self) -> str:
        return f"Pong({self.response})"


class Versions(Response):
    def __init__(self: Self, data: bytes) -> None:
        decoded = data.decode("ascii")
        model, versions = decoded.split(":")
        hw_rev, fw_rev = versions.split(",")

        self.model: str = model
        self.hardware_rev: str = hw_rev.strip()
        self.firmware_rev: str = fw_rev.strip()

    def __str__(self: Self) -> str:
        return (
            f"Versions(model={self.model}, hardware_rev={self.hardware_rev}, "
            f"firmware_rev={self.firmware_rev})"
        )


class PowerResponse(Response):
    def __init__(self: Self, data: bytes) -> None:
        assert_empty(data)

    def __str__(self: Self) -> str:
        return "PowerResponse()"


class ClearedScreen(Response):
    def __init__(self: Self, data: bytes) -> None:
        assert_empty(data)

    def __str__(self: Self) -> str:
        return "ClearedScreen()"


class Line1Set(Response):
    def __init__(self: Self, data: bytes) -> None:
        assert_empty(data)

    def __str__(self: Self) -> str:
        return "Line1Set()"


class Line2Set(Response):
    def __init__(self: Self, data: bytes) -> None:
        assert_empty(data)

    def __str__(self: Self) -> str:
        return "Line2Set()"


class CursorPositionSet(Response):
    def __init__(self: Self, data: bytes) -> None:
        assert_empty(data)

    def __str__(self: Self) -> str:
        return "CursorPositionSet()"


class CursorStyleSet(Response):
    def __init__(self: Self, data: bytes) -> None:
        assert_empty(data)

    def __str__(self: Self) -> str:
        return "CursorStyleSet()"


class ContrastSet(Response):
    def __init__(self: Self, data: bytes) -> None:
        assert_empty(data)

    def __str__(self: Self) -> str:
        return "ContrastSet()"


class BacklightSet(Response):
    def __init__(self: Self, data: bytes) -> None:
        assert_empty(data)

    def __str__(self: Self) -> str:
        return "BacklightSet()"


class StatusResponse(Response):
    def __init__(self: Self, data: bytes) -> None:
        self.data: bytes = data

    def __str__(self: Self) -> str:
        return f"Status({self.data})"


class KeyActivityReport(Response):
    """
    A key activity report from the Crystalfontz LCD.

    Status: Untested
    """

    def __init__(self: Self, data: bytes) -> None:
        assert_len(1, data)

        self.activity: KeyActivity = KeyActivity.from_bytes(data)

    def __str__(self: Self) -> str:
        return f"KeyActivityReport({self.activity.name})"


class TemperatureReport(Response):
    """
    A temperature sensor report from the Crystalfontz LCD.

    Status: Untested
    """

    def __init__(self: Self, data: bytes) -> None:
        assert_len(4, data)

        self.idx: int = data[0]
        value = struct.unpack(">H", data[1:2])[0]
        dow_crc_status = data[3]

        if dow_crc_status == 0:
            raise DecodeError("Bad CRC from temperature sensor")

        self.celsius: float = value / 16.0
        self.fahrenheit: float = (9 / 5 * self.celsius) + 32.0

    def __str__(self: Self) -> str:
        return (
            f"TemperatureReport({self.idx}, celsius={self.celsius}, "
            f"fahrenheit={self.fahrenheit})"
        )


RESPONSE_CLASSES: Dict[int, Type[Response]] = {
    # Command responses start with bits 0b01
    0x40: Pong,
    0x41: Versions,
    0x45: PowerResponse,
    0x46: ClearedScreen,
    0x47: Line1Set,
    0x48: Line2Set,
    0x4B: CursorStyleSet,
    0x4D: ContrastSet,
    0x4E: BacklightSet,
    0x5E: StatusResponse,
    # Reports start with bits 0b10
    0x80: KeyActivityReport,
    0x82: TemperatureReport,
}
