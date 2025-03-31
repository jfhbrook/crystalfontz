from typing import ClassVar, Tuple

from crystalfontz.dbus.map.base import struct
from crystalfontz.device import Device


class DeviceM:
    t: ClassVar[str] = struct("sss")

    @staticmethod
    def pack(device: Device) -> Tuple[str, str, str]:
        return (device.model, device.hardware_rev, device.firmware_rev)


class StatusM:
    t: ClassVar[str] = ""
