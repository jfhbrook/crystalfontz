from typing import ClassVar

from crystalfontz.baud import BaudRate


class BaudRateM:
    t: ClassVar[str] = "q"

    @staticmethod
    def unpack(baud_rate: int) -> BaudRate:
        if baud_rate != 19200 and baud_rate != 115200:
            raise ValueError("baud rate must be 19200 or 115200")
        return baud_rate
