from abc import ABC
from collections import defaultdict
from typing import Any, Dict, Self

from crystalfontz.error import DecodeError

DeviceStatus = Any


class Device(ABC):
    LINE_WIDTH = 16

    def status(self: Self, data: bytes) -> DeviceStatus:
        raise NotImplementedError("parse_status")


class CFA533_H1_4_U1_V2(Device):
    LINE_WIDTH = 16

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

DEVICES: DeviceDict = {
    "CFA533": defaultdict(lambda: defaultdict(lambda: CFA533_H1_4_U1_V2()))
}
