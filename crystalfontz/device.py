from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Dict, Optional, Self
import warnings

from crystalfontz.error import DecodeError

DeviceStatus = Any


class Device(ABC):
    model: str = "<unknown>"
    hardware_rev: str = "<unknown>"
    firmware_rev: str = "<unknown>"

    lines = 2
    columns = 16
    ENHANCED_CONTRAST = False

    @abstractmethod
    def brightness(
        self: Self, lcd_brightness: int, keypad_brightness: Optional[int]
    ) -> bytes:
        raise NotImplementedError("brightness")

    @abstractmethod
    def status(self: Self, data: bytes) -> DeviceStatus:
        raise NotImplementedError("status")


def assert_brightness_in_range(name: str, brightness: int) -> None:
    if brightness < 0:
        raise ValueError(f"{name} brightness {brightness} < 0")
    elif brightness > 100:
        raise ValueError(f"{name} brightness {brightness} > 100")


# INCOMPLETE
class CFA633(Device):
    model: str = "CFA633"
    hardware_rev: str = "h1.5c"
    firmware_rev: str = "k1.7"

    lines = 2
    columns = 16
    ENHANCED_CONTRAST = False

    def brightness(
        self: Self, lcd_brightness: int, keypad_brightness: Optional[int]
    ) -> bytes:
        assert_brightness_in_range("LCD", lcd_brightness)

        if keypad_brightness is not None:
            warnings.warn("CFA633 does not support keypad brightness")

        return lcd_brightness.to_bytes()


class CFA533(Device):
    model = "CFA533"
    hardware_rev = "h1.4"
    firmware_rev = "u1v2"

    lines = 2
    columns = 16
    ENHANCED_CONTRAST = True

    def brightness(
        self: Self, lcd_brightness: int, keypad_brightness: Optional[int]
    ) -> bytes:
        assert_brightness_in_range("LCD", lcd_brightness)
        brightness = lcd_brightness.to_bytes()

        # CFA533 can optionally accept a second parameter for keypad brightness
        if keypad_brightness is not None:
            assert_brightness_in_range("Keypad", keypad_brightness)
            brightness += keypad_brightness.to_bytes()

        return brightness

    def status(self: Self, data: bytes) -> DeviceStatus:
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

        raise NotImplementedError("parse_status")


FirmwareDict = Dict[str, Device]
HardwareDict = Dict[str, FirmwareDict]
DeviceDict = Dict[str, HardwareDict]

DEVICES: DeviceDict = {"CFA533": defaultdict(lambda: defaultdict(lambda: CFA533()))}
