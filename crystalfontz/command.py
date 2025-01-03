from abc import ABC, abstractmethod
from functools import reduce
from typing import Iterable, Optional, Self, Set
import warnings

from crystalfontz.atx import AtxPowerSwitchFunctionalitySettings
from crystalfontz.baud import BaudRate
from crystalfontz.character import SpecialCharacter
from crystalfontz.cursor import CursorStyle
from crystalfontz.device import Device
from crystalfontz.keys import KeyPress
from crystalfontz.packet import Packet
from crystalfontz.temperature import pack_temperature_settings

SET_LINE_WARNING_TEMPLATE = (
    "Command {code} ({code:02x}): {name} is deprecated"
    " in favor of command 31 (0x1F): Send Data to LCD."
)


class Command(ABC):
    @abstractmethod
    def to_packet(self: Self) -> Packet:
        raise NotImplementedError("to_packet")


class Ping(Command):
    command: int = 0x00

    def __init__(self: Self, payload: bytes) -> None:
        if len(payload) > 16:
            raise ValueError(f"Payload length {len(payload)} > 16")
        self.payload: bytes = payload

    def to_packet(self) -> Packet:
        return (self.command, self.payload)


class GetVersions(Command):
    command: int = 0x01

    def to_packet(self: Self) -> Packet:
        return (self.command, b"")


class WriteUserFlash(Command):
    command: int = 0x02

    def to_packet(self: Self) -> Packet:
        raise NotImplementedError("to_packet")


class ReadUserFlash(Command):
    command: int = 0x03

    def to_packet(self: Self) -> Packet:
        raise NotImplementedError("to_packet")


class StoreBootState(Command):
    command: int = 0x04

    def to_packet(self: Self) -> Packet:
        return (self.command, b"")


class PowerCommand(Command):
    command: int = 0x05

    pass


class RebootLCD(PowerCommand):
    def to_packet(self: Self) -> Packet:
        return (self.command, bytes([8, 18, 99]))


class ResetHost(PowerCommand):
    def to_packet(self: Self) -> Packet:
        return (self.command, bytes([12, 28, 97]))


class ShutdownHost(PowerCommand):
    def to_packet(self: Self) -> Packet:
        return (self.command, bytes([3, 11, 95]))


class ClearScreen(Command):
    command: int = 0x06

    def to_packet(self: Self) -> Packet:
        return (self.command, b"")


class SetLine1(Command):
    command: int = 0x07

    def __init__(self: Self, line: str | bytes, device: Device) -> None:
        warnings.warn(
            SET_LINE_WARNING_TEMPLATE.format(
                code=0x07, name="Set LCD Contents, Line 1"
            ),
            DeprecationWarning,
        )
        buffer: bytes = (
            device.character_rom.encode(line) if isinstance(line, str) else line
        )

        if len(buffer) > device.columns:
            raise ValueError(f"Line length {len(buffer)} longer than {device.columns}")

        self.line = buffer.ljust(device.columns, b" ")

    def to_packet(self: Self) -> Packet:
        return (self.command, self.line)


class SetLine2(Command):
    command: int = 0x08

    def __init__(self: Self, line: str | bytes, device: Device) -> None:
        warnings.warn(
            SET_LINE_WARNING_TEMPLATE.format(
                code=0x08, name="Set LCD Contents, Line 2"
            ),
            DeprecationWarning,
        )
        buffer: bytes = (
            device.character_rom.encode(line) if isinstance(line, str) else line
        )

        if len(buffer) > device.columns:
            raise ValueError(f"Line length {len(buffer)} longer than {device.columns}")

        self.line: bytes = buffer.ljust(device.columns, b" ")

    def to_packet(self: Self) -> Packet:
        return (self.command, self.line)


class SetSpecialCharacterData(Command):
    command: int = 0x09

    def __init__(
        self: Self, index: int, character: SpecialCharacter, device: Device
    ) -> None:
        device.character_rom.validate_special_character_index(index)
        self.index: int = index
        self.character: bytes = character.as_bytes(device)

    def to_packet(self: Self) -> Packet:
        data = self.index.to_bytes() + self.character
        assert len(data) == 9
        return (self.command, self.index.to_bytes() + self.character)


class Poke(Command):
    command: int = 0x0A

    def __init__(self: Self, address: int) -> None:
        # Address is native to the LCD controller. On the CFA533 h1.4 u1v2,
        # they are:
        #
        #     [0x40, 0x7F] -> CGRAM
        #     [0x80, 0x93] -> DDRAM, line 1
        #     [0xC0, 0xD3] -> DDRAM, line 2
        #
        # These are likely specific to the model and revision. Rather than
        # attempt to validate these at the Device level, we simply assert
        # that the address is a valid byte, and leave choosing sensible
        # addresses as an exercise for the user.
        if not (0 < address < 255):
            raise ValueError(f"Address {address} is invalid")
        self.address: bytes = address.to_bytes()

    def to_packet(self: Self) -> Packet:
        return (self.command, self.address)


class SetCursorPosition(Command):
    command: int = 0x0B

    def __init__(self: Self, row: int, column: int, device: Device) -> None:
        if column < 0:
            raise ValueError(f"Column {column} < 0")
        elif column >= device.columns:
            raise ValueError(f"Column {column} >= {device.columns}")
        if row < 0:
            raise ValueError(f"Row {row} < 0")
        elif row >= device.lines:
            raise ValueError(f"Row {row} >= {device.lines}")

        self.row = row
        self.column = column

    def to_packet(self: Self) -> Packet:
        return (self.command, self.column.to_bytes() + self.row.to_bytes())


class SetCursorStyle(Command):
    command: int = 0x0C

    def __init__(self, style: CursorStyle) -> None:
        self.style: bytes = style.value.to_bytes()

    def to_packet(self: Self) -> Packet:
        return (self.command, self.style)


class SetContrast(Command):
    command: int = 0x0D

    def __init__(self: Self, contrast: float, device: Device) -> None:
        self.contrast = device.contrast(contrast)

    def to_packet(self: Self) -> Packet:
        return (self.command, self.contrast)


class SetBacklight(Command):
    command: int = 0x0E

    def __init__(
        self: Self,
        lcd_brightness: float,
        keypad_brightness: Optional[float],
        device: Device,
    ) -> None:
        self.brightness = device.brightness(lcd_brightness, keypad_brightness)

    def to_packet(self: Self) -> Packet:
        return (self.command, self.brightness)


# 0x0F-0x11 are reserved


class ReadDowInfo(Command):
    command: int = 0x12

    def to_packet(self: Self) -> Packet:
        raise NotImplementedError("to_packet")


class SetupTemperatureReporting(Command):
    command: int = 0x13

    def __init__(self: Self, enabled: Iterable[int], device: Device) -> None:
        self.settings = pack_temperature_settings(enabled, device)

    def to_packet(self: Self) -> Packet:
        return (self.command, self.settings)


class DowTransaction(Command):
    command: int = 0x14

    def to_packet(self: Self) -> Packet:
        raise NotImplementedError("to_packet")


class SetupTemperatureDisplay(Command):
    command: int = 0x15

    def to_packet(self: Self) -> Packet:
        raise NotImplementedError("to_packet")


class RawCommand(Command):
    command: int = 0x16

    def to_packet(self: Self) -> Packet:
        raise NotImplementedError("to_packet")


def _key_mask(keypresses: Set[KeyPress]) -> int:
    return reduce(lambda mask, keypress: mask ^ keypress, keypresses, 0x00)


class ConfigureKeyReporting(Command):
    command: int = 0x17

    def __init__(
        self: Self, when_pressed: Set[KeyPress], when_released: Set[KeyPress]
    ) -> None:
        self.when_pressed: int = _key_mask(when_pressed)
        self.when_released: int = _key_mask(when_released)

    def to_packet(self: Self) -> Packet:
        return (
            self.command,
            self.when_pressed.to_bytes() + self.when_released.to_bytes(),
        )


class PollKeypad(Command):
    command: int = 0x18

    def to_packet(self: Self) -> Packet:
        return (self.command, b"")


# 0x19-0x1B are reserved


class SetAtxPowerSwitchFunctionality(Command):
    command: int = 0x1C

    def __init__(self: Self, settings: AtxPowerSwitchFunctionalitySettings) -> None:
        self.settings = settings

    def to_packet(self: Self) -> Packet:
        return (self.command, self.settings.to_bytes())


class ConfigureWatchdog(Command):
    command: int = 0x1D

    def to_packet(self: Self) -> Packet:
        raise NotImplementedError("to_packet")


class ReadStatus(Command):
    command: int = 0x1E

    def to_packet(self: Self) -> Packet:
        raise NotImplementedError("to_packet")


class SendData(Command):
    command: int = 0x1F

    def __init__(
        self: Self, row: int, column: int, text: str | bytes, device: Device
    ) -> None:
        if not (0 <= row < device.lines):
            raise ValueError(f"{row} is not a valid row")
        if not (0 <= column < device.columns):
            raise ValueError(f"{column} is not a valid column")

        buffer: bytes = (
            device.character_rom.encode(text) if isinstance(text, str) else text
        )

        if len(buffer) > device.columns:
            raise ValueError(f"Text length {len(buffer)} longer than {device.columns}")

        self.row: int = row
        self.column: int = column
        self.text: bytes = buffer

    def to_packet(self: Self) -> Packet:
        return (self.command, self.column.to_bytes() + self.row.to_bytes() + self.text)


# 0x20 is reserved for CFA631 key legends


class SetBaudRate(Command):
    command: int = 0x21

    def __init__(self: Self, rate: BaudRate) -> None:
        self.baud_rate: int = 0
        if rate == 115200:
            self.baud_rate = 1
        elif rate != 19200:
            raise ValueError(f"Unsupported baud rate {rate}")

    def to_packet(self: Self) -> Packet:
        return (self.command, self.baud_rate.to_bytes())


class ConfigureGpio(Command):
    command: int = 0x22

    def to_packet(self: Self) -> Packet:
        raise NotImplementedError("to_packet")


class ReadGpio(Command):
    command: int = 0x23

    def to_packet(self: Self) -> Packet:
        raise NotImplementedError("to_packet")
