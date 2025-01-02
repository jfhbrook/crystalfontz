from abc import ABC, abstractmethod
import struct
from typing import Dict, Self, Type

from crystalfontz.error import DecodeError
from crystalfontz.keys import KeyActivity
from crystalfontz.packet import Packet


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

        raise DecodeError(f"Unknown response ({code}, {data})")


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


class Status(Response):
    # TODO: Device AND firmware specific
    def __init__(self: Self, data: bytes) -> None:
        if len(data) != 15:
            raise DecodeError(f"Status expected to be 15 bytes, is {len(data)} bytes")
        # data[0] is reserved
        temp_1 = data[1]
        temp_2 = data[2]
        temp_3 = data[3]
        temp_4 = data[4]
        key_presses = data[5]
        key_releases = data[6]
        atx_power = data[7]
        watchdog_counter = data[8]
        contrast_adjust = data[9]
        backlight = data[10]
        sense_on_floppy = data[11]
        # data[12] is reserved
        cfa633_contrast = data[13]
        backlight = data[14]


class SetLine1Response(Response):
    def __init__(self: Self, data: bytes) -> None:
        if len(data) != 0:
            raise DecodeError("Response expected to be 0 bytes, is {len(data)} bytes")


class SetLine2Response(Response):
    def __init__(self: Self, data: bytes) -> None:
        if len(data) != 0:
            raise DecodeError("Response expected to be 0 bytes, is {len(data)} bytes")
        pass


class KeyActivityReport(Response):
    """
    A key activity report from the Crystalfontz LCD.

    Status: Untested
    """

    def __init__(self: Self, data: bytes) -> None:
        self.activity: KeyActivity = KeyActivity.from_bytes(data)

    def __str__(self: Self) -> str:
        return f"KeyActivityReport({self.activity.name})"


class TemperatureReport(Response):
    """
    A temperature sensor report from the Crystalfontz LCD.

    Status: Untested
    """

    def __init__(self: Self, data: bytes) -> None:
        if len(data) != 4:
            raise DecodeError("Temperature report expects 4 bytes of data")
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
    0x40: Pong,
    0x41: Versions,
    0x47: SetLine1Response,
    0x48: SetLine2Response,
    0x5E: Status,
    0x80: KeyActivityReport,
    0x82: TemperatureReport,
}
