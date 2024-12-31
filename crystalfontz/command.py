from enum import Enum
from typing import Self, Type


class Command(Enum):
    PING = 0x00
    GET_VERSIONS = 0x01
    WRITE_USER_FLASH = 0x02
    READ_USER_FLASH = 0x03
    STORE_BOOT_STATE = 0x04
    POWER_CMD = 0x05
    CLEAR = 0x06
    SET_L1 = 0x07
    SET_L2 = 0x08
    SET_SPECIAL = 0x09
    POKE = 0x0A
    SET_CURSOR_POS = 0x0B
    SET_CURSOR_STYLE = 0x0C
    SET_CONTRAST = 0x0D
    SET_BACKLIGHT = 0x0E
    # 0x0F-0x11 are reserved
    READ_DOW_INFO = 0x12
    SETUP_TEMP_REPORT = 0x13
    DOW_TXN = 0x14
    SETUP_TEMP_DISPLAY = 0x15
    RAW_CMD = 0x16
    CONFIG_KEY_REPORT = 0x17
    POLL_KEYPAD = 0x18
    # 0x19-0x1B are reserved
    SET_ATX_SWITCH = 0x1C
    CONFIG_WATCHDOG = 0x1D
    READ_STATUS = 0x1E
    SEND_DATA = 0x1F
    # 0x20 is reserved for CFA631 key legends
    SET_BAUD = 0x21
    CONFIG_GPIO = 0x22
    READ_GPIO = 0x23

    @classmethod
    def to_bytes(cls: Type[Self], cmd: Self) -> bytes:
        return cmd.value.to_bytes()
