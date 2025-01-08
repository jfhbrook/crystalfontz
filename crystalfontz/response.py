from abc import ABC, abstractmethod
import struct
from typing import Any, Callable, cast, Dict, Type, TypeVar

try:
    from typing import Self
except ImportError:
    Self = Any

from crystalfontz.error import (
    DecodeError,
    DeviceError,
    ResponseDecodeError,
    UnknownResponseError,
)
from crystalfontz.gpio import GpioSettings, GpioState
from crystalfontz.keys import KeyActivity, KeyStates
from crystalfontz.packet import Packet


def assert_len(n: int, data: bytes) -> None:
    if len(data) != n:
        raise DecodeError(f"Response expected to be {n} bytes, is {len(data)} bytes")


class Response(ABC):
    """
    A response received from the Crystalfontz LCD.

    To implement a new response type, subclass this class and implement the
    __init__ method.
    """

    @abstractmethod
    def __init__(self: Self, data: bytes) -> None:
        raise NotImplementedError("__init__")

    @classmethod
    def from_packet(cls: Type[Self], packet: Packet) -> "Response":
        code, data = packet
        if code in RESPONSE_CLASSES:
            res_cls = RESPONSE_CLASSES[code]
            try:
                return res_cls(data)
            except Exception as exc:
                raise ResponseDecodeError(res_cls, str(exc)) from exc

        if DeviceError.is_error_code(code):
            raise DeviceError(packet)

        raise UnknownResponseError(packet)


class RawResponse(Response):
    """
    A raw response. This class may be used with `client.expect` to capture
    an otherwise unsupported response type.
    """

    def __init__(self: Self, data: bytes) -> None:
        self.code: int = 0xFF
        self.data: bytes = data

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


def code(code: int) -> Callable[[Type[R]], Type[R]]:
    def decorator(cls: Type[R]) -> Type[R]:
        RESPONSE_CLASSES[code] = cast(Type[Response], cls)
        return cls

    return decorator


@code(0x40)
class Pong(Response):
    """
    Attributes:
        response (bytes): The data sent in the ping command.
    """

    def __init__(self: Self, data: bytes) -> None:
        self.response = data

    def __str__(self: Self) -> str:
        return f"Pong({self.response})"


@code(0x41)
class Versions(Response):
    """
    Attributes:
        model (str): The device model.
        hardware_rev (str): The device's hardware revision.
        firmware_rev (str): The device's firmware revision.
    """

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
    """
    Attributes:
        data (bytes): The data read from the user flash area.
    """

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
class LcdMemory(Response):
    """
    Attributes:
        address (int): The address read from LCD memory.
        data (bytes): The data read from the address in LCD memory.
    """

    def __init__(self: Self, data: bytes) -> None:
        assert_len(9, data)
        self.address: int = data[0]
        self.data: bytes = data[1:]

    def __str__(self: Self) -> str:
        return f"LcdMemory(0x{self.address:02X}={self.data})"


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
    """
    Attributes:
        index (int): The DOW device index.
        rom_id (bytes): The ROM ID of the device.
    """

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
class DowTransactionResult(Response):
    """
    Attributes:
        index (int): The DOW device index.
        data (bytes): Data read from the 1-wire bus.
        crc (int): The 1-wire CRC.
    """

    def __init__(self: Self, data: bytes) -> None:
        self.index = data[0]
        self.data = data[1:-1]
        self.crc = data[-1]

    def __str__(self: Self) -> str:
        return f"DowTransactionResult({self.index}, data={self.data}, crc={self.crc})"


@code(0x55)
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
    """
    Attributes:
        states (KeyStates): The keypad's key states.
    """

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
    """
    A raw status response. This status is parsed based on the device.
    """

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


@code(0x62)
class GpioSet(Ack):
    def __str__(self: Self) -> str:
        return "GpioSet()"


@code(0x63)
class GpioRead(Response):
    """
    Attributes:
        index (int): The index of the GPIO pin.
        state (GpioState): Pin state & changes since last poll.
        requested_level (int): Requested Pin level/PWM level.
        settings (GpioSettings): Pin function select and drive mode.
    """

    def __init__(self: Self, data: bytes) -> None:
        self.index: int = data[0]
        self.state: GpioState = GpioState.from_byte(data[1])
        self.requested_level: int = data[2]
        self.settings: GpioSettings = GpioSettings.from_byte(data[3])

    def __str__(self: Self) -> str:
        return (
            f"GpioRead({self.index}, state={self.state}, "
            f"requested_level={self.requested_level}, settings={self.settings}"
        )


@code(0x80)
class KeyActivityReport(Response):
    """
    A key activity report from the Crystalfontz LCD.

    Attributes:
        activity (KeyActivity): The reported key activity.
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

    Attributes:
        index (int): The index of the temperature sensor.
        celsius (float): The temperature in celsius.
        fahrenheit (float): The temperature in fahrenheit.
    """

    def __init__(self: Self, data: bytes) -> None:
        assert_len(4, data)

        self.index: int = data[0]
        value = struct.unpack(">H", data[1:3])[0]
        dow_crc_status = data[3]

        if dow_crc_status == 0:
            raise DecodeError("Bad CRC from temperature sensor")

        self.celsius: float = value / 16.0
        self.fahrenheit: float = (9 / 5 * self.celsius) + 32.0

    def __str__(self: Self) -> str:
        return (
            f"TemperatureReport({self.index}, celsius={self.celsius}, "
            f"fahrenheit={self.fahrenheit})"
        )
