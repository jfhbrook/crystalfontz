from typing import Dict, Literal

BaudRate = Literal[19200] | Literal[115200]

SLOW_BAUD_RATE: BaudRate = 19200
FAST_BAUD_RATE: BaudRate = 115200

OTHER_BAUD_RATE: Dict[BaudRate, BaudRate] = {
    SLOW_BAUD_RATE: FAST_BAUD_RATE,
    FAST_BAUD_RATE: SLOW_BAUD_RATE,
}
