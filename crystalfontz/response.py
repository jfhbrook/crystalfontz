from abc import ABC, abstractmethod
import struct
from typing import Callable, cast, Dict, Self, Type, TypeVar

from crystalfontz.error import DecodeError, DeviceError, UnknownResponseError
from crystalfontz.keys import KeyActivity, KeyStates
from crystalfontz.packet import Packet


def assert_len(n: int, data: bytes) -> None:
    if len(data) != n:
        raise DecodeError(f"Response expected to be {n} bytes, is {len(data)} bytes")


class Response(ABC):
    """
    A response received from the Crystalfontz LCD.
    """

    @abstractmethod
    def __init__(self: Self, data: bytes) -> None:
        raise NotImplementedError("__init__")

    @classmethod
    def from_packet(cls: Type[Self], packet: Packet) -> "Response":
        code, data = packet
        if code in RESPONSE_CLASSES:
            return RESPONSE_CLASSES[code](data)

        if DeviceError.is_error_code(code):
            raise DeviceError(packet)

        raise UnknownResponseError(packet)


class RawResponse(Response):
    def __init__(self: Self, data: bytes) -> None:
        self.code: int = 0xFF
        self.data = data

    @classmethod
    def from_packet(cls: Type[Self], packet: Packet) -> Self:
        code, data = packet
        res = cls(data)
        res.code = code
        return res


class Ack(Response):
    def __init__(self: Self, data: bytes) -> None:
        assert_len(0, data)

    def __str__(self: Self) -> str:
        return "Ack()"


RESPONSE_CLASSES: Dict[int, Type[Response]] = {}

R = TypeVar("R", bound=Response)


def code[R](code: int) -> Callable[[Type[R]], Type[R]]:
    def decorator(cls: Type[R]) -> Type[R]:
        RESPONSE_CLASSES[code] = cast(Type[Response], cls)
        return cls

    return decorator


@code(0x40)
class Pong(Response):
    def __init__(self: Self, data: bytes) -> None:
        self.response = data

    def __str__(self: Self) -> str:
        return f"Pong({self.response})"


@code(0x41)
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


@code(0x42)
class UserFlashAreaWritten(Ack):
    def __str__(self: Self) -> str:
        return "UserFlashAreaWritten()"


@code(0x43)
class UserFlashAreaRead(Response):
    def __init__(self: Self, data: bytes) -> None:
        self.data: bytes = data

    def __str__(self: Self) -> str:
        return f"UserFlashAreaRead({self.data})"


@code(0x44)
class BootStateStored(Ack):
    def __str__(self: Self) -> str:
        return "BootStateStored()"


@code(0x45)
class PowerResponse(Ack):
    def __str__(self: Self) -> str:
        return "PowerResponse()"


@code(0x46)
class ClearedScreen(Ack):
    def __str__(self: Self) -> str:
        return "ClearedScreen()"


@code(0x47)
class Line1Set(Ack):
    def __str__(self: Self) -> str:
        return "Line1Set()"


@code(0x48)
class Line2Set(Ack):
    def __str__(self: Self) -> str:
        return "Line2Set()"


@code(0x49)
class SpecialCharacterDataSet(Ack):
    def __str__(self: Self) -> str:
        return "SpecialCharacterDataSet()"


@code(0x4A)
class Poked(Response):
    def __init__(self: Self, data: bytes) -> None:
        assert_len(9, data)
        self.address: int = data[0]
        self.data: bytes = data[1:]

    def __str__(self: Self) -> str:
        return f"Poked(0x{self.address:02X}={self.data})"


@code(0x4B)
class CursorPositionSet(Ack):
    def __str__(self: Self) -> str:
        return "CursorPositionSet()"


@code(0x4C)
class CursorStyleSet(Ack):
    def __str__(self: Self) -> str:
        return "CursorStyleSet()"


@code(0x4D)
class ContrastSet(Ack):
    def __str__(self: Self) -> str:
        return "ContrastSet()"


@code(0x4E)
class BacklightSet(Ack):
    def __str__(self: Self) -> str:
        return "BacklightSet()"


@code(0x52)
class DowDeviceInformation(Response):
    def __init__(self: Self, data: bytes) -> None:
        self.index: int = data[0]
        self.rom_id: bytes = data[1:]

    def __str__(self: Self) -> str:
        return f"DownDeviceInformation({self.index}={self.rom_id})"


@code(0x53)
class TemperatureReportingSetUp(Ack):
    def __str__(self: Self) -> str:
        return "TemperatureReportingSetUp()"


@code(0x54)
class LiveTemperatureDisplaySetUp(Ack):
    def __str__(self: Self) -> str:
        return "LiveTemperatureDisplaySetUp"


@code(0x56)
class CommandSentToLcdController(Ack):
    def __str__(self: Self) -> str:
        return "CommandSentToLcdController()"


@code(0x57)
class KeyReportingConfigured(Ack):
    def __str__(self: Self) -> str:
        return "KeyReportingConfigured()"


@code(0x58)
class KeypadPolled(Response):
    def __init__(self: Self, data: bytes) -> None:
        assert_len(3, data)
        self.states = KeyStates.from_bytes(data)

    def __str__(self: Self) -> str:
        return f"KeypadPolled(states={self.states})"


@code(0x5C)
class AtxPowerSwitchFunctionalitySet(Ack):
    def __str__(self: Self) -> str:
        return "AtxPowerFunctionalitySet()"


@code(0x5D)
class WatchdogConfigured(Ack):
    def __str__(self: Self) -> str:
        return "WatchdogConfigured()"


@code(0x5E)
class StatusRead(Response):
    def __init__(self: Self, data: bytes) -> None:
        self.data: bytes = data

    def __str__(self: Self) -> str:
        return f"StatusRead({self.data})"


@code(0x5F)
class DataSent(Ack):
    def __str__(self: Self) -> str:
        return "DataSent()"


@code(0x61)
class BaudRateSet(Ack):
    def __str__(self: Self) -> str:
        return "BaudRateSet()"


@code(0x80)
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


@code(0x82)
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
