from abc import ABC, abstractmethod
from typing import Optional, Self
import warnings

from crystalfontz.character import encode_chars
from crystalfontz.cursor import CursorStyle
from crystalfontz.device import Device
from crystalfontz.packet import Packet

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

    def __init__(self: Self, line: str, device: Device) -> None:
        warnings.warn(
            SET_LINE_WARNING_TEMPLATE.format(
                code=0x07, name="Set LCD Contents, Line 1"
            ),
            DeprecationWarning,
        )

        buffer = encode_chars(line)
        self.line = buffer.ljust(device.columns, b" ")

    def to_packet(self: Self) -> Packet:
        return (self.command, self.line)


class SetLine2(Command):
    command: int = 0x08

    def __init__(self: Self, line: str, device: Device) -> None:
        warnings.warn(
            SET_LINE_WARNING_TEMPLATE.format(
                code=0x08, name="Set LCD Contents, Line 2"
            ),
            DeprecationWarning,
        )
        buffer = encode_chars(line)
        self.line = buffer.ljust(device.columns, b" ")

    def to_packet(self: Self) -> Packet:
        return (self.command, self.line)


class SetSpecialCharacterData(Command):
    command: int = 0x09

    def to_packet(self: Self) -> Packet:
        raise NotImplementedError("to_packet")


class Poke(Command):
    command: int = 0x0A

    def to_packet(self: Self) -> Packet:
        raise NotImplementedError("to_packet")


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


class SetupTemperatureReport(Command):
    command: int = 0x13

    def to_packet(self: Self) -> Packet:
        raise NotImplementedError("to_packet")


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


class ConfigKeyReport(Command):
    command: int = 0x17

    def to_packet(self: Self) -> Packet:
        raise NotImplementedError("to_packet")


class PollKeypad(Command):
    command: int = 0x18

    def to_packet(self: Self) -> Packet:
        raise NotImplementedError("to_packet")


# 0x19-0x1B are reserved


class SetAtxPower(Command):
    command: int = 0x1C

    def to_packet(self: Self) -> Packet:
        raise NotImplementedError("to_packet")


class ConfigWatchdog(Command):
    command: int = 0x1D

    def to_packet(self: Self) -> Packet:
        raise NotImplementedError("to_packet")


class ReadStatus(Command):
    command: int = 0x1E

    def to_packet(self: Self) -> Packet:
        raise NotImplementedError("to_packet")


class SendData(Command):
    command: int = 0x1F

    def to_packet(self: Self) -> Packet:
        raise NotImplementedError("to_packet")


# 0x20 is reserved for CFA631 key legends


class SetBaud(Command):
    command: int = 0x21

    def to_packet(self: Self) -> Packet:
        raise NotImplementedError("to_packet")


class ConfigGpio(Command):
    command: int = 0x22

    def to_packet(self: Self) -> Packet:
        raise NotImplementedError("to_packet")


class ReadGpio(Command):
    command: int = 0x23

    def to_packet(self: Self) -> Packet:
        raise NotImplementedError("to_packet")
