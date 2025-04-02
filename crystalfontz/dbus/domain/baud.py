from typing import ClassVar

from crystalfontz.baud import BaudRate
from crystalfontz.dbus.domain.base import Uint16M

BaudRateT = int


class BaudRateM:
    t: ClassVar[str] = Uint16M.t

    @staticmethod
    def unpack(baud_rate: BaudRateT) -> BaudRate:
        if baud_rate != 19200 and baud_rate != 115200:
            raise ValueError("baud rate must be 19200 or 115200")
        return baud_rate
