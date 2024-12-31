from abc import ABC, abstractmethod
import struct
from typing import Dict, Self, Type

from crystalfontz.error import ParseError
from crystalfontz.keys import KeyActivity
from crystalfontz.packet import Packet


class Report(ABC):
    """
    A report received from the Crystalfontz LCD.
    """

    @abstractmethod
    def __init__(self, data: bytes) -> None:
        raise NotImplementedError("__init__")

    @classmethod
    def from_packet(cls: Type[Self], packet: Packet) -> "Report":
        code, data = packet
        if code in REPORT_CLASSES:
            return REPORT_CLASSES[code](data)

        raise ParseError(f"Unknown report code {code}")


class KeyActivityReport(Report):
    """
    A key activity report from the Crystalfontz LCD.

    Status: Untested
    """

    def __init__(self, data: bytes) -> None:
        self.activity: KeyActivity = KeyActivity.from_bytes(data)

    def __str__(self) -> str:
        return f"KeyActivityReport({self.activity.name})"


class TemperatureReport(Report):
    """
    A temperature sensor report from the Crystalfontz LCD.

    Status: Untested
    """

    def __init__(self, data: bytes) -> None:
        if len(data) != 4:
            raise ParseError("Temperature report expects 4 bytes of data")
        self.sensor_idx: int = data[0]
        value = struct.unpack(">H", data[1:2])[0]
        dow_crc_status = data[3]

        if dow_crc_status == 0:
            raise ParseError("Bad CRC from temperature sensor")

        self.celsius: float = value / 16.0
        self.fahrenheit: float = (9 / 5 * self.celsius) + 32.0


REPORT_CLASSES: Dict[int, Type[Report]] = {
    0x80: KeyActivityReport,
    0x82: TemperatureReport,
}
