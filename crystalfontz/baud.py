from typing import Literal

BaudRate = Literal[19200] | Literal[115200]

SLOW_BAUD_RATE: BaudRate = 19200
FAST_BAUD_RATE: BaudRate = 115200
