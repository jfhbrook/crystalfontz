from abc import ABC, abstractmethod
import warnings

from crystalfontz.character import encode_chars
from crystalfontz.device import Device, DEVICES
from crystalfontz.error import EncodeError
from crystalfontz.packet import Packet

SET_LINE_WARNING_TEMPLATE = (
    "Command {code} ({code:02x}): {name} is deprecated"
    " in favor of command 31 (0x1F): Send Data to LCD."
)


class Command(ABC):
    @abstractmethod
    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")


class Ping(Command):
    command: int = 0x00

    def __init__(self, payload: bytes) -> None:
        if len(payload) > 16:
            raise EncodeError(f"Payload length {len(payload)} > 16")
        self.payload: bytes = payload

    def to_packet(self) -> Packet:
        return (self.command, self.payload)


class GetVersions(Command):
    command: int = 0x01

    def to_packet(self) -> Packet:
        return (self.command, b"")


class WriteUserFlash(Command):
    command: int = 0x02

    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")


class ReadUserFlash(Command):
    command: int = 0x03

    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")


class PowerCommand(Command):
    command: int = 0x05

    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")


class ClearScreen(Command):
    command: int = 0x06

    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")


class SetLine1(Command):
    command: int = 0x07

    def __init__(self, line: str, device: Device) -> None:
        warnings.warn(
            SET_LINE_WARNING_TEMPLATE.format(
                code=0x07, name="Set LCD Contents, Line 1"
            ),
            DeprecationWarning,
        )

        buffer = encode_chars(line)
        self.line = buffer.ljust(device.LINE_WIDTH, b" ")

    def to_packet(self) -> Packet:
        return (self.command, self.line)


class SetLine2(Command):
    command: int = 0x08

    def __init__(self, line: str, device: Device) -> None:
        warnings.warn(
            SET_LINE_WARNING_TEMPLATE.format(
                code=0x08, name="Set LCD Contents, Line 2"
            ),
            DeprecationWarning,
        )
        buffer = encode_chars(line)
        self.line = buffer.ljust(device.LINE_WIDTH, b" ")

    def to_packet(self) -> Packet:
        return (self.command, self.line)


class SetSpecialCharacterData(Command):
    command: int = 0x09

    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")


class Poke(Command):
    command: int = 0x0A

    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")


class SetCursorPosition(Command):
    command: int = 0x0B

    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")


class SetCursorStyle(Command):
    command: int = 0x0C

    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")


class SetContrast(Command):
    command: int = 0x0  #

    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")


class SetBacklight(Command):
    command: int = 0x0E

    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")


# 0x0F-0x11 are reserved


class ReadDowInfo(Command):
    command: int = 0x12

    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")


class SetupTemperatureReport(Command):
    command: int = 0x13

    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")


class DowTransaction(Command):
    command: int = 0x14

    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")


class SetupTemperatureDisplay(Command):
    command: int = 0x15

    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")


class RawCommand(Command):
    command: int = 0x16

    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")


class ConfigKeyReport(Command):
    command: int = 0x17

    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")


class PollKeypad(Command):
    command: int = 0x18

    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")


# 0x19-0x1B are reserved


class SetAtxPower(Command):
    command: int = 0x1C

    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")


class ConfigWatchdog(Command):
    command: int = 0x1D

    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")


class ReadStatus(Command):
    command: int = 0x1E

    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")


class SendData(Command):
    command: int = 0x1F

    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")


# 0x20 is reserved for CFA631 key legends


class SetBaud(Command):
    command: int = 0x21

    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")


class ConfigGpio(Command):
    command: int = 0x22

    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")


class ReadGpio(Command):
    command: int = 0x23

    def to_packet(self) -> Packet:
        raise NotImplementedError("to_packet")
