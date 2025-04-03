from abc import ABC, abstractmethod
from dataclasses import asdict
import struct
import textwrap
from typing import Any, Callable, cast, Dict, Self, Type, TypeVar

from crystalfontz.error import (
    DecodeError,
    DeviceError,
    ResponseDecodeError,
    UnknownResponseError,
)
from crystalfontz.format import format_bytes, format_json_bytes
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

    @classmethod
    @abstractmethod
    def from_bytes(cls: Type[Self], data: bytes) -> Self:
        raise NotImplementedError("from_bytes")

    @classmethod
    def from_packet(cls: Type[Self], packet: Packet) -> "Response":
        code, data = packet
        if code in RESPONSE_CLASSES:
            res_cls = RESPONSE_CLASSES[code]
            try:
                return res_cls.from_bytes(data)
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
    @classmethod
    def from_bytes(cls: Type[Self], data: bytes) -> Self:
        assert_len(0, data)
        return cls()

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

    def __init__(self: Self, response: bytes) -> None:
        self.response = response

    @classmethod
    def from_bytes(cls: Type[Self], data: bytes) -> Self:
        return cls(data)

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

    def __init__(self: Self, model: str, hardware_rev: str, firmware_rev: str) -> None:
        self.model: str = model
        self.hardware_rev: str = hardware_rev
        self.firmware_rev: str = firmware_rev

    @classmethod
    def from_bytes(cls: Type[Self], data: bytes) -> Self:
        decoded = data.decode("ascii")
        model, versions = decoded.split(":")
        hw_rev, fw_rev = versions.split(",")

        return cls(model, hw_rev.strip(), fw_rev.strip())

    def __str__(self: Self) -> str:
        return (
            f"Versions(model={self.model}, hardware_rev={self.hardware_rev}, "
            f"firmware_rev={self.firmware_rev})"
        )

    def as_dict(self: Self) -> Dict[str, Any]:
        return dict(
            model=self.model,
            hardware_rev=self.hardware_rev,
            firmware_rev=self.firmware_rev,
        )

    def __repr__(self: Self) -> str:
        return f"{self.model}: {self.hardware_rev}, {self.firmware_rev}"


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

    @classmethod
    def from_bytes(cls: Type[Self], data: bytes) -> Self:
        return cls(data)

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

    def __init__(self: Self, address: int, data: bytes) -> None:
        self.address: int = address
        self.data: bytes = data

    @classmethod
    def from_bytes(cls: Type[Self], data: bytes) -> Self:
        assert_len(9, data)
        address: int = data[0]
        lcd_data: bytes = data[1:]

        return cls(address, lcd_data)

    def __str__(self: Self) -> str:
        return f"LcdMemory(0x{self.address:02X}={self.data})"

    def as_dict(self: Self) -> Dict[str, Any]:
        return dict(address=self.address, data=format_json_bytes(self.data))

    def __repr__(self: Self) -> str:
        return f"0x{self.address:02X}: {format_bytes(self.data)}"


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

    def __init__(self: Self, index: int, rom_id: int) -> None:
        self.index: int = index
        self.rom_id: int = rom_id

    @classmethod
    def from_bytes(cls: Type[Self], data: bytes) -> Self:
        index: int = data[0]
        rom_id: int = int.from_bytes(data[1:], "big")
        return cls(index, rom_id)

    def __str__(self: Self) -> str:
        return f"DowDeviceInformation({self.index:02X}={self.rom_id:02X})"

    def as_dict(self: Self) -> Dict[str, Any]:
        return dict(index=self.index, rom_id=self.rom_id)

    def __repr__(self: Self) -> str:
        return f"0x{self.index:02X}: {self.rom_id:02X}"


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

    def __init__(self: Self, index: int, data: bytes, crc: int) -> None:
        self.index = index
        self.data = data
        self.crc = crc

    @classmethod
    def from_bytes(cls: Type[Self], data: bytes) -> Self:
        index = data[0]
        txn_data = data[1:-1]
        crc = data[-1]

        return cls(index, txn_data, crc)

    def __str__(self: Self) -> str:
        return (
            f"DowTransactionResult(0x{self.index:02X}, "
            f"data={self.data}, crc={self.crc})"
        )

    def as_dict(self: Self) -> Dict[str, Any]:
        return dict(index=self.index, data=format_json_bytes(self.data), crc=self.crc)

    def __repr__(self: Self) -> str:
        repr_ = f"Transaction Result for Device {self.index}:\n"
        repr_ += f"  Data: {format_bytes(self.data)}\n"
        repr_ += f"  CRC: 0x{self.crc:02X}"
        return repr_


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

    def __init__(self: Self, states: KeyStates) -> None:
        self.states = states

    @classmethod
    def from_bytes(cls: Type[Self], data: bytes) -> Self:
        assert_len(3, data)
        states = KeyStates.from_bytes(data)
        return cls(states)

    def __str__(self: Self) -> str:
        return f"KeypadPolled(states={self.states})"

    def as_dict(self: Self) -> Dict[str, Any]:
        return dict(states=asdict(self.states))

    def __repr__(self: Self) -> str:
        repr_ = "Keypad States:\n"
        repr_ += textwrap.indent(repr(self.states), "  ")

        return repr_


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

    @classmethod
    def from_bytes(cls: Type[Self], data: bytes) -> Self:
        return cls(data)

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

    def __init__(
        self: Self,
        index: int,
        state: GpioState,
        requested_level: int,
        settings: GpioSettings,
    ) -> None:
        self.index: int = index
        self.state: GpioState = state
        self.requested_level: int = requested_level
        self.settings: GpioSettings = settings

    @classmethod
    def from_bytes(cls: Type[Self], data: bytes) -> Self:
        index: int = data[0]
        state: GpioState = GpioState.from_byte(data[1])
        requested_level: int = data[2]
        settings: GpioSettings = GpioSettings.from_byte(data[3])

        return cls(index, state, requested_level, settings)

    def __str__(self: Self) -> str:
        return (
            f"GpioRead({self.index}, state={self.state}, "
            f"requested_level={self.requested_level}, settings={self.settings}"
        )

    def as_dict(self: Self) -> Dict[str, Any]:
        return dict(
            index=self.index,
            state=asdict(self.state),
            requested_level=self.requested_level,
            settings=self.settings.as_dict(),
        )

    def __repr__(self: Self) -> str:
        repr_ = f"GPIO pin {self.index}:\n"
        repr_ += f"  Requested Level: {self.requested_level}\n"
        repr_ += "  Settings:\n"
        repr_ += textwrap.indent(repr(self.settings), "    ")
        return repr_


@code(0x80)
class KeyActivityReport(Response):
    """
    A key activity report from the Crystalfontz LCD.

    Attributes:
        activity (KeyActivity): The reported key activity.
    """

    def __init__(self: Self, activity: KeyActivity) -> None:
        self.activity: KeyActivity = activity

    @classmethod
    def from_bytes(cls: Type[Self], data: bytes) -> Self:
        assert_len(1, data)

        activity: KeyActivity = KeyActivity.from_bytes(data)

        return cls(activity)

    def __str__(self: Self) -> str:
        return f"KeyActivityReport({self.activity.name})"

    def __repr__(self: Self) -> str:
        return f"{self.__class__.__name__}\t{self.activity.name}"

    def as_dict(self: Self) -> Dict[str, Any]:
        return dict(type=self.__class__.__name__, activity=self.activity.name)


@code(0x82)
class TemperatureReport(Response):
    """
    A temperature sensor report from the Crystalfontz LCD.

    Attributes:
        index (int): The index of the temperature sensor.
        celsius (float): The temperature in celsius.
        fahrenheit (float): The temperature in fahrenheit.
    """

    def __init__(self: Self, index: int, celsius: float, fahrenheit: float) -> None:
        self.index: int = index
        self.celsius: float = celsius
        self.fahrenheit: float = fahrenheit

    @classmethod
    def from_bytes(cls: Type[Self], data: bytes) -> Self:
        assert_len(4, data)

        index: int = data[0]
        value = struct.unpack(">H", data[1:3])[0]
        dow_crc_status = data[3]

        if dow_crc_status == 0:
            raise DecodeError("Bad CRC from temperature sensor")

        celsius: float = value / 16.0
        fahrenheit: float = (9 / 5 * celsius) + 32.0

        return cls(index, celsius, fahrenheit)

    def __str__(self: Self) -> str:
        return (
            f"TemperatureReport({self.index}, celsius={self.celsius}, "
            f"fahrenheit={self.fahrenheit})"
        )

    def __repr__(self: Self) -> str:
        return f"{self.__class__.__name__}\t{self.celsius}\t{self.fahrenheit}"

    def as_dict(self: Self) -> Dict[str, Any]:
        return dict(
            type=self.__class__.__name__,
            celsius=self.celsius,
            fahrenheit=self.fahrenheit,
        )
