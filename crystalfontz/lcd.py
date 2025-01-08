from enum import Enum


class LcdRegister(Enum):
    """
    An LCD register. The LCD supports two registers, "DATA" and "CONTROL".
    """

    DATA = 0
    CONTROL = 1
